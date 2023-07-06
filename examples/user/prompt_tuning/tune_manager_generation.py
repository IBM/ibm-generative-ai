import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.schemas.tunes_params import CreateTuneParams, TunesListParams
from genai.services.tune_manager import TuneManager

load_dotenv()
API_KEY = os.getenv("GENAI_KEY", None)
ENDPOINT = os.getenv("GENAI_API", None)

creds = Credentials(api_key=API_KEY, api_endpoint=ENDPOINT)

file_ids = ["<some-file-id>"]

## Testing generation task

params = CreateTuneParams(
    name="flan-t5-xl",
    model_id="google/flan-t5-xl",
    method_id="pt",
    task_id="generation",
    training_file_ids=file_ids,
)


# Create tune
tune_create = TuneManager.create_tune(credentials=creds, params=params)
print("\n\nNew tune: \n", tune_create)

tune_id = tune_create.id

params = TunesListParams(limit=5, offset=0)

# List tunes
tune_list = TuneManager.list_tunes(credentials=creds, params=params)
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
