import os

from dotenv import load_dotenv

from genai.services import ServiceInterface

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()

SERVICE_URL = "https://workbench-api.res.ibm.com/v1/"
GENAI_KEY = os.getenv("GENAI_KEY")
service = ServiceInterface(service_url=SERVICE_URL, api_key=GENAI_KEY)
completion = service.generate("google/ul2", ["hello! How are you?"])
print(completion)
