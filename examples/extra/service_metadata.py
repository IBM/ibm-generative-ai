"""
Retrieve metadata for given service method

From metadat you can see for instance which endpoint does the method uses.
"""

from dotenv import load_dotenv

from genai import Client, Credentials
from genai.utils import get_service_action_metadata

load_dotenv()

credentials = Credentials.from_env()
client = Client(credentials=credentials)

metadata = get_service_action_metadata(client.text.generation.create)
print(metadata.model_dump())
