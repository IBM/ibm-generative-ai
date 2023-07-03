import os

from dotenv import load_dotenv
from genai.credentials import Credentials

from genai_prompt_tuning.schemas import CreateTuneParams, TunesListParams
from genai_prompt_tuning.tune_manager import TuneManager

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

TUNE_MANAGER = TuneManager(credentials=creds)

# Create tune
tune_create = TUNE_MANAGER.create_tune(params)
print("\n\nNew tune: \n", tune_create)

tune_id = tune_create.id

params = TunesListParams(limit=5, offset=0)

# List tunes
tune_list = TUNE_MANAGER.list_tunes(params)
print("\n\nList of tunes: \n", tune_list)

# Get a tune
tune_get = TUNE_MANAGER.get_tune(tune_id)
print("\n\nGet tune result: \n", tune_get)

# Delete a tune
tune_delete = TUNE_MANAGER.delete_tune(tune_id)
print("\n\nDelete tune response:", tune_delete)
