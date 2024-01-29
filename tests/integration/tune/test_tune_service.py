import json
import time
from pathlib import Path
from typing import NamedTuple

import pytest

from genai import Client
from genai.schema import FilePurpose, TuneAssetType, TuneStatus, TuningType

TEST_MODEL_ID = "google/flan-t5-xl"
TUNE_NAME = "test_tune"

TRAIN_FILE_PATH = Path(__file__).parent / Path("datasets/neurips_impact_statement_risks/test_tune_train.json")
VAL_FILE_PATH = Path(__file__).parent / Path("datasets/neurips_impact_statement_risks/test_tune_validate.json")


class TuneData(NamedTuple):
    train_file_id: str
    test_file_id: str


@pytest.mark.integration
class TestTuneService:
    def _download_data(self):
        """This function can be used to re-download the dataset in datasets/ folder, requires `datasets` package"""
        from datasets import load_dataset

        dataset = load_dataset("ought/raft", "neurips_impact_statement_risks")
        labels_mapping = dataset["train"].features["Label"].names

        def map_line(line: dict):
            return {
                "input": f'Paper Title: {line["Paper title"]}; Impact statement: {line["Impact statement"]}',
                "output": labels_mapping[line["Label"]],
            }

        train_val_split = 40
        train_lines = [map_line(line) for line in dataset["train"]]
        with open(TRAIN_FILE_PATH, "w") as f:
            json.dump(train_lines[:train_val_split], f, indent=2)
        with open(VAL_FILE_PATH, "w") as f:
            json.dump(train_lines[train_val_split:], f, indent=2)

    @pytest.fixture
    def prepare_data(self, client):
        if not TRAIN_FILE_PATH.exists() or not VAL_FILE_PATH.exists():
            self._download_data()

        train_file_id = client.file.create(TRAIN_FILE_PATH, purpose=FilePurpose.TUNE).result.id
        test_file_id = client.file.create(VAL_FILE_PATH, purpose=FilePurpose.TUNE).result.id
        try:
            yield TuneData(train_file_id, test_file_id)
        finally:
            client.file.delete(id=train_file_id)
            client.file.delete(id=test_file_id)

    @pytest.mark.vcr
    def test_create_retrieve_delete_tune(self, client: Client, prepare_data: TuneData, subtests, vcr):
        is_recording = not vcr.write_protected
        with subtests.test("Create Tune"):
            tune_create_response = client.tune.create(
                name=TUNE_NAME,
                task_id="classification",
                model_id=TEST_MODEL_ID,
                tuning_type=TuningType.PROMPT_TUNING,
                training_file_ids=[prepare_data.train_file_id],
            )
            tune_id = tune_create_response.result.id

        with subtests.test("Wait for tune to finish (retrieve)"):
            # wait for task finish
            while True:
                retrieve_response = client.tune.retrieve(id=tune_id)
                if retrieve_response.result.status in {TuneStatus.COMPLETED, TuneStatus.HALTED, TuneStatus.FAILED}:
                    break
                if is_recording:
                    time.sleep(30)
            assert retrieve_response.result.status == TuneStatus.COMPLETED
            assert retrieve_response.result.id == tune_id
            assert retrieve_response.result.training_files[0].id == prepare_data.train_file_id

        with subtests.test("Read tune response"):
            tune_logs = client.tune.read(id=tune_id, type=TuneAssetType.LOGS)
            assert isinstance(tune_logs, bytes) and tune_logs

            tune_export = client.tune.read(id=tune_id, type=TuneAssetType.EXPORT)
            assert isinstance(tune_export, bytes) and tune_export

            tune_vectors = client.tune.read(id=tune_id, type=TuneAssetType.VECTORS)
            assert isinstance(tune_vectors, bytes) and tune_vectors

        with subtests.test("List tune"):
            tunes = client.tune.list(search=TUNE_NAME).results
            assert any(tune.id == tune_id for tune in tunes)

        with subtests.test("Delete tune"):
            client.tune.delete(tune_id)

    @pytest.mark.vcr
    def test_tune_types(self, client: Client):
        tune_types = client.tune.types().results
        assert any(TEST_MODEL_ID in tune_type.model_ids for tune_type in tune_types)
