"""
Tune a custom model (Prompt Tuning)

Use custom training data to tune a model for text classification.

Note:
    This example has been written to enable an end-user to quickly try prompt-tuning. In order to obtain better
    performance, a user would need to experiment with the number of observations and tuning hyperparameters
"""

import time
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import (
    DecodingMethod,
    FilePurpose,
    TextGenerationParameters,
    TuneAssetType,
    TuneParameters,
    TuneStatus,
    TuningType,
)

load_dotenv()
num_training_samples = 100
num_validation_samples = 20
data_root = Path(__file__).parent.resolve() / ".data"
training_file = data_root / "fpb_train.jsonl"
validation_file = data_root / "fpb_validation.jsonl"


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


def create_dataset():
    Path(data_root).mkdir(parents=True, exist_ok=True)
    if training_file.exists() and validation_file.exists():
        print("Dataset is already prepared")
        return

    try:
        import pandas as pd
        from datasets import load_dataset
    except ImportError:
        print("Please install datasets and pandas for downloading the dataset.")
        raise

    data = load_dataset("financial_phrasebank", "sentences_allagree")
    df = pd.DataFrame(data["train"]).sample(n=num_training_samples + num_validation_samples)
    df.rename(columns={"sentence": "input", "label": "output"}, inplace=True)
    df["output"] = df["output"].astype(str)
    train_jsonl = df.iloc[:num_training_samples].to_json(orient="records", lines=True, force_ascii=True)
    validation_jsonl = df.iloc[num_training_samples:].to_json(orient="records", lines=True, force_ascii=True)
    with open(training_file, "w") as fout:
        fout.write(train_jsonl)
    with open(validation_file, "w") as fout:
        fout.write(validation_jsonl)


def upload_files(client: Client, update=True):
    files_info = client.file.list(search=training_file.name).results
    files_info += client.file.list(search=validation_file.name).results

    filenames_to_id = {f.file_name: f.id for f in files_info}
    for filepath in [training_file, validation_file]:
        filename = filepath.name
        if filename in filenames_to_id and update:
            print(f"File already present: Overwriting {filename}")
            client.file.delete(filenames_to_id[filename])
            response = client.file.create(file_path=filepath, purpose=FilePurpose.TUNE)
            filenames_to_id[filename] = response.result.id
        if filename not in filenames_to_id:
            print(f"File not present: Uploading {filename}")
            response = client.file.create(file_path=filepath, purpose=FilePurpose.TUNE)
            filenames_to_id[filename] = response.result.id
    return filenames_to_id[training_file.name], filenames_to_id[validation_file.name]


client = Client(credentials=Credentials.from_env())

print(heading("Creating dataset"))
create_dataset()

print(heading("Uploading files"))
training_file_id, validation_file_id = upload_files(client, update=True)

hyperparams = TuneParameters(num_epochs=2, verbalizer='classify { "0", "1", "2" } Input: {{input}} Output:')

print(heading("Tuning model"))
tune_result = client.tune.create(
    model_id="google/flan-t5-xl",
    name="classification-mpt-tune-api",
    tuning_type=TuningType.PROMPT_TUNING,
    task_id="classification",  # Another supported task is "summarization"
    parameters=hyperparams,
    training_file_ids=[training_file_id],
    # validation_file_ids=[validation_file_id], # TODO: Broken at the moment - this causes tune to fail
).result

while tune_result.status not in [TuneStatus.FAILED, TuneStatus.HALTED, TuneStatus.COMPLETED]:
    new_tune_result = client.tune.retrieve(tune_result.id).result
    print(f"Waiting for tune to finish, current status: {tune_result.status}")
    tune_result = new_tune_result
    time.sleep(10)

if tune_result.status in [TuneStatus.FAILED, TuneStatus.HALTED]:
    print("Model tuning failed or halted")
    exit(1)

print(heading("Classify with a tuned model"))
prompt = "Return on investment was 5.0 % , compared to a negative 4.1 % in 2009 ."
print("Prompt: ", prompt)
gen_params = TextGenerationParameters(decoding_method=DecodingMethod.SAMPLE, max_new_tokens=1, min_new_tokens=1)
gen_response = next(client.text.generation.create(model_id=tune_result.id, inputs=[prompt]))
print("Answer: ", gen_response.results[0].generated_text)

print(heading("Get list of tuned models"))
interesting_metadata_fields = ["name", "id", "model_id", "created_at", "status"]
tune_list = client.tune.list(limit=5, offset=0)
for tune in tune_list.results:
    pprint(tune.model_dump(include=interesting_metadata_fields))


print(heading("Retrieve metadata for a single tune"))
tune_detail = client.tune.retrieve(id=tune_result.id).result
pprint(tune_detail.model_dump(include=interesting_metadata_fields + ["parameters"]))

print(heading("Downloading tune model assets"))
logs = client.tune.read(id=tune_result.id, type=TuneAssetType.LOGS).decode("utf-8")
print(logs)

print(heading("Deleting a tuned model"))
client.tune.delete(tune_result.id)
print("OK")
