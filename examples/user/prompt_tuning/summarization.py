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
from genai.services import FileManager, TuneManager

load_dotenv()
num_training_samples = 100
num_validation_samples = 20
data_root = Path(__file__).parent.resolve() / "data"
training_file = data_root / "summarization_train.jsonl"
validation_file = data_root / "summarization_validation.jsonl"


def create_dataset():
    Path(data_root).mkdir(parents=True, exist_ok=True)
    if training_file.exists() and validation_file.exists():
        return
    data = load_dataset("cnn_dailymail", "3.0.0")
    jsondict = {}
    samples = {"train": num_training_samples, "validation": num_validation_samples}
    for split in ["train", "validation"]:
        df = pd.DataFrame(data[split]).sample(n=samples[split])
        df.rename(columns={"article": "input", "highlights": "output"}, inplace=True)
        df = df[["input", "output"]]
        df["output"] = df["output"].astype(str)
        jsondict[split] = df
    train_jsonl = jsondict["train"].to_json(orient="records", lines=True, force_ascii=True)
    validation_jsonl = jsondict["validation"].to_json(orient="records", lines=True, force_ascii=True)
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
    hyperparams = CreateTuneHyperParams(num_epochs=2, verbalizer="Input: {{input}} Output:")
    training_file_ids, validation_file_ids = get_file_ids(creds)

    tuned_model = model.tune(
        name="summarization-mpt-tune-api",
        method="mpt",
        task="summarization",
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
            prompt = input("Enter a prompt:\n")
            genparams = GenerateParams(
                decoding_method="greedy",
                max_new_tokens=50,
                min_new_tokens=1,
            )
            tuned_model.params = genparams
            print("Answer = ", tuned_model.generate([prompt])[0].generated_text)

            print("~~~~~~~ Listing tunes with TuneManager ~~~~~")

            list_params = TunesListParams(limit=5, offset=0)

            tune_list = TuneManager.list_tunes(credentials=creds, params=list_params)
            print("\n\nList of tunes: \n\n")
            for tune in tune_list.results:
                print(tune, "\n")

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
