"""
Show information about supported models
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


print(heading("List all models"))
for model in client.model.list(limit=100).results:
    print(model.model_dump(include=["name", "id"]))

print(heading("Get model detail"))
model_detail = client.model.retrieve("google/flan-t5-xl").result
pprint(model_detail.model_dump(include=["name", "description", "id", "developer", "size"]))
