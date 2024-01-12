"""Show information about current user"""

from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

print(heading("Get user info"))
user_info = client.user.retrieve().result
pprint(user_info.model_dump())

print(heading("Accept terms of use and give data usage consent"))
user_update_info = client.user.update(tou_accepted=True).result
pprint(user_update_info.model_dump())
