import os
from pathlib import Path

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.schemas.tunes_params import CreateTuneParams
from genai.services import FileManager, TuneManager

load_dotenv()
API_KEY = os.getenv("GENAI_KEY", None)
ENDPOINT = os.getenv("GENAI_API", None)

creds = Credentials(api_key=API_KEY, api_endpoint=ENDPOINT)

# # UPLOAD FILE
# file_path = "<path-to-file>"
print("======================== UPLOAD LOCAL FILE ========================")
file_path = str(Path(__file__).parent / "file_to_tune.jsonl")
print(" {} \n".format(file_path))

upload_file = FileManager.upload_file(credentials=creds, file_path=file_path, purpose="tune")
print("File uploaded: \n", upload_file)

print("\n===================== GET UPLOADED FILE ID ========================")
file_list = FileManager.list_files(credentials=creds)
for f in file_list.results:
    if f.file_name == "file_to_tune.jsonl":
        file_id = f.id
        break
print("Uploaded file has id = {}\n".format(file_id))

print("\n================= CREATE TUNE FOR GENERATION TASK ==================")

tunes_params = CreateTuneParams(
    name="flan-t5-xl",
    model_id="google/flan-t5-xl",
    method_id="pt",
    task_id="generation",
    training_file_ids=[file_id],
)

tune_create = TuneManager.create_tune(credentials=creds, params=tunes_params)
print("Created tune has the id: \n ", tune_create.id)
