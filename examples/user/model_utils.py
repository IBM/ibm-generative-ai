import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<your-genai-api endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint=api_url)

print("======= List of all models =======")
for m in Model.models(credentials=creds):
    print(m)

print("====== Checking model availability =======")
model = Model("google/ul2", params=None, credentials=creds)
print("Model availability for 'google/ul2': ", model.available())

model = Model("random", params=None, credentials=creds)
print("Model availability for 'random': ", model.available())

print("====== Display model card =======")
model = Model("google/ul2", params=None, credentials=creds)
print("Model info for 'google/ul2': \n", model.info())
