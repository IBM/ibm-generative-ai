import os
from pathlib import Path

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.schemas import FileListParams
from genai.services import FileManager

load_dotenv()
API_KEY = os.getenv("GENAI_KEY", None)
ENDPOINT = os.getenv("GENAI_API", None)

creds = Credentials(api_key=API_KEY, api_endpoint=ENDPOINT)
params = FileListParams(limit=5, offset=0)

# LIST FILES
print("-------- Listing files ----------")
file_list = FileManager.list_files(credentials=creds, params=params)
for f in file_list.results:
    print(f, "\n")

# GET METADATA
file_id = file_list.results[0].id
print("-------- File metadata with id = {} --------".format(file_id))
file_metadata = FileManager.file_metadata(credentials=creds, file_id=file_id)
print("File Metadada: \n", file_metadata)

# READ FILE
print("------- Read a file with id = {} -----".format(file_id))
file_content = FileManager.read_file(credentials=creds, file_id=file_id)
print("File content: \n", file_content)

# # UPLOAD FILE
# file_path = "<path-to-file>"
file_path = str(Path(__file__).parent / "file_to_tune.jsonl")
print("------- Uploading local file {} ------".format(file_path))
upload_file = FileManager.upload_file(credentials=creds, file_path=file_path, purpose="tune")
print("File uploaded: \n", upload_file)

file_list = FileManager.list_files(credentials=creds, params=params)
for f in file_list.results:
    if f.file_name == "file_to_tune.jsonl":
        file_id = f.id
        break
print("Uploaded file has id = {}\n".format(file_id))

# DELETE FILE
file_id_to_delete = "<some-file-id>"
print("-------- Deleting the above uploaded file -------")
file_delete = FileManager.delete_file(credentials=creds, file_id=file_id)
print("RESPONSE DELETE: \n", file_delete)
