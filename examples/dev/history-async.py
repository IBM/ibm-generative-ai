import asyncio
import os

from dotenv import load_dotenv

from genai.schemas.history_params import HistoryParams
from genai.services import ServiceInterface

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()

api_key = os.getenv("GENAI_KEY")
SERVICE_URL = "https://workbench-api.res.ibm.com/v1/"

service = ServiceInterface(service_url=SERVICE_URL, api_key=api_key)
model = "google/ul2"
inputs = ["Hello! How are you today?"]

params = HistoryParams(
    limit=8,
    offset=0,
    status="SUCCESS",
    origin="API",
)

print("\n------------- Example (Async History)-------------\n")


async def app() -> None:
    async_history = await service.async_history(params=params)
    async_history = async_history.json()
    print(async_history)


if __name__ == "__main__":
    asyncio.run(app())
