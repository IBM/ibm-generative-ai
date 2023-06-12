import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import ModelType, TokenParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

print("\n------------- Example (Async Greetings)-------------\n")

params = TokenParams(return_tokens=True)

creds = Credentials(api_key, api_endpoint)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

greeting = "Hello! How are you?"
lots_of_greetings = [greeting] * 100
num_of_greetings = len(lots_of_greetings)
num_said_greetings = 0
greeting1 = "Hello! How are you?"

# yields batch of results that are produced asynchronously and in parallel
for result in model.tokenize_async(lots_of_greetings):
    num_said_greetings += 1
    print(f"[Progress {str(float(num_said_greetings/num_of_greetings)*100)}%]")
    print(f"\t {result}")
