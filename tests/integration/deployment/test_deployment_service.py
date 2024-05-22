import json
import time
from pathlib import Path

import pytest

from genai import Client
from genai.schema import DeploymentStatus, FilePurpose, TuneParameters, TuneStatus

TEST_MODEL_ID = "meta-llama/llama-3-8b-instruct"
TUNE_NAME = "test_tune"

TRAIN_FILE_PATH = Path(__file__).parent / Path("datasets/test_fine_tune_train.jsonl")


@pytest.mark.integration
class TestDeploymentService:
    def _download_data(self):
        """This function can be used to re-download the dataset in datasets/ folder, requires `datasets` package"""
        from datasets import load_dataset

        dataset = load_dataset("locuslab/TOFU")

        def map_line(line: dict):
            return {
                "input": line["question"],
                "output": line["answer"],
            }

        train_val_split = 50
        cut_dataset = list(dataset["train"])[:train_val_split]
        train_lines = [map_line(line) for line in cut_dataset]
        with open(TRAIN_FILE_PATH, "w") as f:
            json.dump(train_lines, f, indent=2)

    @pytest.fixture
    def prepare_tune_id(self, client: Client):
        if not TRAIN_FILE_PATH.exists():
            self._download_data()
        train_file_id = client.file.create(TRAIN_FILE_PATH, purpose=FilePurpose.TUNE).result.id
        hyperparams = TuneParameters(
            num_epochs=4,
            verbalizer="### Input: {{input}} ### Response: {{output}}",
            batch_size=4,
            learning_rate=0.4,
            per_device_eval_batch_size=4,
            gradient_accumulation_steps=4,
            per_device_train_batch_size=4,
            num_train_epochs=4,
        )
        tune_create_response = client.tune.create(
            name=TUNE_NAME,
            task_id="generation",
            model_id=TEST_MODEL_ID,
            tuning_type="fine_tuning",
            training_file_ids=[train_file_id],
            parameters=hyperparams,
        )
        return tune_create_response.result.id

    @pytest.mark.vcr
    def test_create_retrieve_delete_deployment(self, client: Client, prepare_tune_id: str, subtests, vcr) -> None:
        is_recording = not vcr.write_protected
        # wait for tune to finish
        while True:
            retrieve_response = client.tune.retrieve(id=prepare_tune_id)
            if retrieve_response.result.status in {TuneStatus.COMPLETED, TuneStatus.HALTED, TuneStatus.FAILED}:
                break
            if is_recording:
                time.sleep(30)
        assert retrieve_response.result.status == TuneStatus.COMPLETED

        with subtests.test("Create deployment"):
            deployment = client.deployment.create(tune_id=prepare_tune_id)
            assert deployment.result.tune_id == prepare_tune_id
            deployment_id = deployment.result.id
            # wait for deployment to finish
            while True:
                deployment = client.deployment.retrieve(id=deployment_id)
                if deployment.result.status in {
                    DeploymentStatus.READY,
                    DeploymentStatus.FAILED,
                    DeploymentStatus.EXPIRED,
                }:
                    break
                if is_recording:
                    time.sleep(30)
        deployment_id = deployment.result.id
        assert deployment.result.status == DeploymentStatus.READY
        assert deployment.result.tune_id == prepare_tune_id

        with subtests.test("List deployments"):
            deployments = client.deployment.list()
            assert any(deployment.id == deployment_id for deployment in deployments.results)

        with subtests.test("Delete deployment and tune"):
            client.deployment.delete(deployment_id)
            client.tune.delete(prepare_tune_id)
