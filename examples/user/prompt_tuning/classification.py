#
# NOTE: This example has been written to enable an end-user
# to quickly try prompt-tuning. In order to obtain better
# performance, a user would need to experiment with the
# number of observations and tuning hyperparameters
#

import os
import time
from pathlib import Path

try:
    from datasets import load_dataset
except ImportError:
    print("Install datasets: it is a pre-requisite to run this example")

try:
    import pandas as pd
except ImportError:
    print("Install pandas: it is a pre-requisite to run this example")

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas.generate_params import GenerateParams
from genai.schemas.tunes_params import CreateTuneHyperParams, TunesListParams
from genai.services import FileManager
from genai.services.tune_manager import TuneManager

load_dotenv()
num_training_samples = 100
num_validation_samples = 20
data_root = Path(__file__).parent.resolve() / "data"
training_file = data_root / "fpb_train.jsonl"
validation_file = data_root / "fpb_validation.jsonl"


def create_dataset():
    Path(data_root).mkdir(parents=True, exist_ok=True)
    if training_file.exists() and validation_file.exists():
        return
    data = load_dataset(
        "financial_phrasebank",
        "sentences_allagree",
    )
    df = pd.DataFrame(data["train"]).sample(n=num_training_samples + num_validation_samples)
    df.rename(columns={"sentence": "input", "label": "output"}, inplace=True)
    df["output"] = df["output"].astype(str)
    train_jsonl = df.iloc[:num_training_samples].to_json(orient="records", lines=True, force_ascii=True)
    validation_jsonl = df.iloc[num_training_samples:].to_json(orient="records", lines=True, force_ascii=True)
    with open(training_file, "w") as fout:
        fout.write(train_jsonl)
    with open(validation_file, "w") as fout:
        fout.write(validation_jsonl)


def upload_files(creds, update=True):
    fileinfos = FileManager.list_files(credentials=creds).results
    filenames_to_id = {f.file_name: f.id for f in fileinfos}
    for filepath in [training_file, validation_file]:
        filename = filepath.name
        if update and filename in filenames_to_id:
            print(f"File already present: Overwriting {filename}")
            FileManager.delete_file(credentials=creds, file_id=filenames_to_id[filename])
            FileManager.upload_file(credentials=creds, file_path=str(filepath), purpose="tune")
        if filename not in filenames_to_id:
            print(f"File not present: Uploading {filename}")
            FileManager.upload_file(credentials=creds, file_path=str(filepath), purpose="tune")


def get_file_ids(creds):
    fileinfos = FileManager.list_files(credentials=creds).results
    training_file_ids = [f.id for f in fileinfos if f.file_name == training_file.name]
    validation_file_ids = [f.id for f in fileinfos if f.file_name == validation_file.name]
    return training_file_ids, validation_file_ids


def get_creds():
    api_key = os.getenv("GENAI_KEY", None)
    endpoint = os.getenv("GENAI_API", None)
    creds = Credentials(api_key=api_key, api_endpoint=endpoint)
    return creds


if __name__ == "__main__":
    creds = get_creds()
    create_dataset()
    upload_files(creds, update=True)

    model = Model("google/flan-t5-xl", params=None, credentials=creds)
    hyperparams = CreateTuneHyperParams(num_epochs=2, verbalizer='classify { "0", "1", "2" } Input: {{input}} Output:')
    training_file_ids, validation_file_ids = get_file_ids(creds)

    tuned_model = model.tune(
        name="classification-mpt-tune-api",
        method="mpt",
        task="classification",
        hyperparameters=hyperparams,
        training_file_ids=training_file_ids,
        validation_file_ids=validation_file_ids,
    )

    status = tuned_model.status()
    while status not in ["FAILED", "HALTED", "COMPLETED"]:
        print(status)
        time.sleep(20)
        status = tuned_model.status()
    else:
        if status in ["FAILED", "HALTED"]:
            print("Model tuning failed or halted")
        else:
            print("Model info:\n")
            print(tuned_model.info())
            time.sleep(5)

            prompt = input("Enter a prompt:\n")
            genparams = GenerateParams(
                decoding_method="greedy",
                max_new_tokens=50,
                min_new_tokens=1,
            )
            print("Answer = ", tuned_model.generate([prompt])[0].generated_text)
            time.sleep(5)

            print("~~~~~~~ List of all models ~~~~~~")
            for m in Model.models(credentials=creds):
                print(m, "\n")
            time.sleep(10)

            print("~~~~~~~ Getting list of all tuned models with TuneManager ~~~~~")

            list_params = TunesListParams(limit=50, offset=0)

            tune_list = TuneManager.list_tunes(credentials=creds, params=list_params)
            print("\n\nList of tunes: \n\n")
            for tune in tune_list.results:
                print(tune, "\n")
            time.sleep(10)

            tune_get_result = TuneManager.get_tune(credentials=creds, tune_id=tuned_model.model)
            print(
                "\n\n~~~~~ Metadata for a single tune with TuneManager ~~~~: \n\n",
                tune_get_result,
            )
            time.sleep(5)

            print("~~~~~~~ Downloading tuned model assets ~~~~~")
            to_download_assets = input("Download tuned model assets? (y/N):\n")
            if to_download_assets == "y":
                tuned_model.download()

            time.sleep(5)

            print("~~~~~~~ Deleting a tuned model ~~~~~")
            to_delete = input("Delete this model? (y/N):\n")
            if to_delete == "y":
                tuned_model.delete()
