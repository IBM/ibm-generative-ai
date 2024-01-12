"""
Working with files

The following example shows how to create/retrieve/read/delete a file from API.
"""

import os
import tempfile
from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client, Credentials
from genai.file import FileSortBy, SortDirection

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()

client = Client(credentials=Credentials.from_env())


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


with tempfile.NamedTemporaryFile(delete=True, suffix=".json") as tmp:
    content = '{"input": "<input>", "output": "<ideal output>"}'
    tmp.write(content.encode())
    tmp.seek(0)

    filename = os.path.basename(tmp.name)

    print(heading("Upload file"))
    upload_result = client.file.create(file_path=tmp.name, purpose="tune")
    file_id = upload_result.result.id
    print(f"File ID: {file_id}")

    try:
        print(heading("List files"))
        for file in client.file.list(
            limit=5,
            search=filename,
            sort_by=FileSortBy.CREATED_AT,
            direction=SortDirection.DESC,
        ).results:
            pprint(file.model_dump())

        print(heading("Get file metadata"))
        metadata_result = client.file.retrieve(file_id).result
        pprint(metadata_result.model_dump())

        print(heading("Get file content"))
        print(client.file.read(file_id))
    finally:
        print(heading("Delete file"))
        client.file.delete(file_id)
        print("OK")
