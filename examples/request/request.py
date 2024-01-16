"""
Working with your requests

The following example shows how to list your requests,
delete a request or a whole chat conversation (group of requests).
"""

from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.request import RequestEndpoint, RequestOrigin, RequestStatus

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

print(heading("History of my requests"))
for history_item in client.request.list(
    limit=8,
    offset=0,
    status=RequestStatus.SUCCESS,
    origin=RequestOrigin.API,
    endpoint=RequestEndpoint.GENERATE,
).results:
    pprint(history_item.model_dump(include=["request", "created_at", "duration"]))

# Deletes a request
# client.request.delete(request_id)

# Deletes a whole chat conversation
# client.request.chat_delete(conversation_id)
