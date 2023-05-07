import os

from dotenv import load_dotenv

from genai import Credentials, Metadata
from genai.schemas.history_params import HistoryParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)

print("\n------------- Example (History)-------------\n")

creds = Credentials(api_key)
object = Metadata(creds)

params = HistoryParams(
    limit=8,
    offset=0,
    status="SUCCESS",
    origin="API",
)

history_response = object.get_history(params)
print(f"Response: \n{history_response}\n")
