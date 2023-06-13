import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.metadata import Metadata
from genai.schemas.history_params import HistoryParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

print("\n------------- Example (History)-------------\n")

creds = Credentials(api_key, api_endpoint)
object = Metadata(creds)

params = HistoryParams(
    limit=8,
    offset=0,
    status="SUCCESS",
    origin="API",
)

history_response = object.get_history(params)
print(f"Response: \n{history_response}\n")
