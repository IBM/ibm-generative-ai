import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.schemas.tunes_params import (
    CreateTuneHyperParams,
    CreateTuneParams,
    TunesListParams,
)
from genai.services.tune_manager import TuneManager

load_dotenv()
API_KEY = os.getenv("GENAI_KEY", None)
ENDPOINT = os.getenv("GENAI_API", None)

creds = Credentials(api_key=API_KEY, api_endpoint=ENDPOINT)

file_ids = ["a7ace3e4-cf43-4930-a1a0-a6003f20ec7f"]  # ["<some-file-id>"]

hyperparams = CreateTuneHyperParams(verbalizer='classify { "red", "yellow" } Input: {{input}} Output:')

params = CreateTuneParams(
    name="flan-t5-xl-red-yellow-TEST-3",
    model_id="google/flan-t5-xl",
    method_id="mpt",
    task_id="classification",
    training_file_ids=file_ids,
    parameters=hyperparams,
)

# Create tune
tune_create = TuneManager.create_tune(credentials=creds, params=params)
print("\n\nNew tune: \n", tune_create)

tune_id = tune_create.id

list_params = TunesListParams(limit=5, offset=0)

# List tunes
tune_list = TuneManager.list_tunes(credentials=creds, params=list_params)
print("\n\nList of tunes: \n", tune_list)

# Get a tune
tune_get = TuneManager.get_tune(credentials=creds, tune_id=tune_id)
print("\n\nGet tune result: \n", tune_get)

# Delete a tune
tune_delete = TuneManager.delete_tune(credentials=creds, tune_id=tune_id)
print("\n\nDelete tune response: \n", tune_delete)

# Get tune methods
tune_methods = TuneManager.get_tune_methods(credentials=creds)
print("\n\nTune methods: \n", tune_methods)

# Download tune assets
# tune_assets =
