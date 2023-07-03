import os

from dotenv import load_dotenv
from genai.credentials import Credentials

from genai_prompt_tuning.schemas import (
    CreateTuneHyperParams,
    CreateTuneParams,
    TunesListParams,
)
from genai_prompt_tuning.tune_manager import TuneManager

load_dotenv()
API_KEY = os.getenv("GENAI_KEY", None)
ENDPOINT = os.getenv("GENAI_API", None)

creds = Credentials(api_key=API_KEY, api_endpoint=ENDPOINT)

file_ids = ["96e9ccba-567f-457f-99d1-4fd3ab44fbf5"]

hyperparams = CreateTuneHyperParams(verbalizer='classify { "red", "yellow" } Input: {{input}} Output:')

params = CreateTuneParams(
    name="flan-t5-xl-red-yellow-TEST-3",
    model_id="google/flan-t5-xl",
    method_id="mpt",
    task_id="classification",
    training_file_ids=file_ids,
    parameters=hyperparams,
)

TUNE_MANAGER = TuneManager(credentials=creds)

# Create tune
tune_create = TUNE_MANAGER.create_tune(params)
print("\n\nNew tune: \n", tune_create)

tune_id = tune_create.id

list_params = TunesListParams(limit=5, offset=0)

# List tunes
tune_list = TUNE_MANAGER.list_tunes(list_params)
print("\n\nList of tunes: \n", tune_list)

# Get a tune
tune_get = TUNE_MANAGER.get_tune(tune_id)
print("\n\nGet tune result: \n", tune_get)

# Delete a tune
# tune_delete = TUNE_MANAGER.delete_tune(tune_id)
# print("\n\nDelete tune response:", tune_delete)
