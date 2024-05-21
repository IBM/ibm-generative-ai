"""
Fine tune and deploy custom model

Use custom training data to tune a model for text generation.

Note:
    This example has been written to enable an end-user to quickly try fine-tuning. In order to obtain better
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
    DeploymentStatus,
    FilePurpose,
    TextGenerationParameters,
    TuneParameters,
    TuneStatus,
)

load_dotenv()
num_training_samples = 50
num_validation_samples = 20
data_root = Path(__file__).parent.resolve() / ".data"
training_file = data_root / "fpb_train.jsonl"
validation_file = data_root / "fpb_validation.jsonl"


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


def create_dataset():
    Path(data_root).mkdir(parents=True, exist_ok=True)
    if training_file.exists():
        print("Dataset is already prepared")
        return

    try:
        import pandas as pd
        from datasets import load_dataset
    except ImportError:
        print("Please install datasets and pandas for downloading the dataset.")
        raise

    data = load_dataset("locuslab/TOFU")
    df = pd.DataFrame(data["train"])
    df.rename(columns={"question": "input", "answer": "output"}, inplace=True)
    df["output"] = df["output"].astype(str)
    train_jsonl = df.iloc[:num_training_samples].to_json(orient="records", lines=True, force_ascii=True)
    validation_jsonl = df.iloc[-num_validation_samples:].to_json(orient="records", lines=True, force_ascii=True)
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

hyperparams = TuneParameters(
    num_epochs=4,
    verbalizer="### Input: {{input}} ### Response: {{output}}",
    batch_size=4,
    learning_rate=0.4,
    # Advanced parameters are not defined in the schema
    # but can be passed to the API
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    per_device_train_batch_size=4,
    num_train_epochs=4,
)
print(heading("Tuning model"))

tune_result = client.tune.create(
    model_id="meta-llama/llama-3-8b-instruct",
    name="generation-fine-tune-example",
    tuning_type="fine_tuning",
    task_id="generation",
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

print("Model tuned successfully")

print(heading("Deploying fine-tuned model"))

deployment = client.deployment.create(tune_id=tune_result.id).result

while deployment.status not in [DeploymentStatus.READY, DeploymentStatus.FAILED, DeploymentStatus.EXPIRED]:
    deployment = client.deployment.retrieve(id=deployment.id).result
    print(f"Waiting for deployment to finish, current status: {deployment.status}")
    time.sleep(10)

if deployment.status in [DeploymentStatus.FAILED, DeploymentStatus.EXPIRED]:
    print("Model deployment failed or expired")
    exit(1)

print("Model deployed successfully")

print(heading("Generate text with fine-tuned model"))
prompt = "What are some books you would reccomend to read?"
print("Prompt: ", prompt)
gen_params = TextGenerationParameters(decoding_method=DecodingMethod.SAMPLE)
gen_response = next(client.text.generation.create(model_id=tune_result.id, inputs=[prompt]))
print("Answer: ", gen_response.results[0].generated_text)

print(heading("Get list of deployed models"))
deployment_list = client.deployment.list()
for deployment in deployment_list.results:
    pprint(deployment.model_dump())

print(heading("Retrieving information about deployment"))
deployment_info = client.deployment.retrieve(id=deployment.id)
pprint(deployment_info.model_dump())

print(heading("Deleting deployment and tuned model"))
client.deployment.delete(id=deployment.id)
client.tune.delete(id=tune_result.id)
print("Deleted")
