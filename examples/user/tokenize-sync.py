import os

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import ModelType, TokenParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)

print("\n------------- Example (Tokenize)-------------\n")

creds = Credentials(api_key)
model = Model(ModelType.FLAN_UL2, params=TokenParams, credentials=creds)

sentence = "Hello! How are you?"

tokenized_response = model.tokenize([sentence], return_tokens=True)
print(f"Tokenized response: {tokenized_response}")
