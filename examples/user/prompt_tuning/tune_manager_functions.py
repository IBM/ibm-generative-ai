import os
from pathlib import Path

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.schemas.tunes_params import (
    CreateTuneHyperParams,
    CreateTuneParams,
    DownloadAssetsParams,
    TunesListParams,
)
from genai.services import FileManager, TuneManager

load_dotenv()
API_KEY = os.getenv("GENAI_KEY", None)
ENDPOINT = os.getenv("GENAI_API", None)

creds = Credentials(api_key=API_KEY, api_endpoint=ENDPOINT)


print("\n=============== UPLOAD LOCAL FILE FOR TUNING ================")
file_path = str(Path(__file__).parent / "file_to_tune.jsonl")
print(" {} \n".format(file_path))

file_uploaded = FileManager.upload_file(credentials=creds, file_path=file_path, purpose="tune")
print("File uploaded: \n", file_uploaded)


print("\n======================== CREATE TUNE ========================")
file_ids = [file_uploaded.id]
hyperparams = CreateTuneHyperParams(verbalizer='classify { "red", "yellow" } Input: {{input}} Output:')

params = CreateTuneParams(
    name="Tune Manager Classification",
    model_id="google/flan-t5-xl",
    method_id="mpt",
    task_id="classification",
    training_file_ids=file_ids,
    parameters=hyperparams,
)

tune_created = TuneManager.create_tune(credentials=creds, params=params)
print("\nNew tune: \n", tune_created)


print("\n======================= GET TUNE BY ID ======================")
t = tune_created.id
tune_get = TuneManager.get_tune(credentials=creds, tune_id=t)
print("\nGet tune result: \n", tune_get)

print("\n======================== LIST TUNES =========================")
list_params = TunesListParams(limit=5, offset=0)
tune_list = TuneManager.list_tunes(credentials=creds, params=list_params)
for t in tune_list.results:
    print("\nTune ID:", t.id, ", Tune Name:", t.name)


print("\n================  LIST EXISTING TUNE METHODS ================")
tune_methods = TuneManager.get_tune_methods(credentials=creds)
print("\n Available Tune Methods:\n")
for t in tune_methods.results:
    print("Method ID:", t.id, ", Method name:", t.name)


print("\n===================  DOWNLOAD TUNE ASSETS ===================")
# content can be: logs or enconder. The download will only be available when the tune is complete.
tune = tune_list.results[0].id
assets_params = DownloadAssetsParams(id=tune, content="encoder")
tune_assets = TuneManager.download_tune_assets(credentials=creds, params=assets_params)
print("\n Tune assets:", tune_assets)


print("\n======================== DELETE TUNE ========================")
tune_delete = TuneManager.delete_tune(credentials=creds, tune_id=tune)
print("\nDelete tune response: \n", tune_delete)
