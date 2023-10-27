import os
import tempfile

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.schemas import FileListParams
from genai.services import FileManager

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
credentials = Credentials(api_key, api_endpoint)

print("\n------------- Example (Working with files)-------------\n")

with tempfile.NamedTemporaryFile(delete=True, suffix=".json") as tmp:
    content = '{"input": "<input>", "output": "<ideal output>"}'
    tmp.write(content.encode())
    tmp.seek(0)

    filename = os.path.basename(tmp.name)

    upload_result = FileManager.upload_file(file_path=tmp.name, purpose="tune", credentials=credentials)
    try:
        files = FileManager.list_files(credentials=credentials, params=FileListParams(search=filename))
        assert files.totalCount == 1
        assert len(files.results) == 1
        metadata = FileManager.file_metadata(upload_result.id, credentials=credentials)
        assert metadata.file_name == filename
        assert metadata.bytes > 0
        assert content == FileManager.read_file(upload_result.id, credentials=credentials)
    finally:
        FileManager.delete_file(upload_result.id, credentials=credentials)
