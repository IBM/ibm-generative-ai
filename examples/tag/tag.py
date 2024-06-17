"""
Working with tags
"""

from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import TagType

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

print(heading("Show all existing tags"))
for tag in client.tag.list(
    limit=100,  # optional
    offset=0,  # optional
    type=TagType.LANGUAGE,  # optional
).results:
    pprint(tag.model_dump())
