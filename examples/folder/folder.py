"""
Working with folders
"""

from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
client = Client(credentials=Credentials.from_env())


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


print(heading("Create a new folder"))
create_response = client.folder.create(name="My folder")
folder_id = create_response.result.id
print(f"Folder ID: {folder_id}")

print(heading("Get the folder details"))
retrieve_response = client.folder.retrieve(id=folder_id)
pprint(retrieve_response.result.model_dump())

print(heading("Show all existing folders"))
list_response = client.folder.list(offset=0, limit=10)
print("Total Count: ", list_response.total_count)
print("Results: ", list_response.results)

print(heading("Delete the folder"))
client.folder.delete(id=folder_id)
print("OK")
