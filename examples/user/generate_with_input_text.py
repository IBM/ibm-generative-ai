import os

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import GenerateParams, ModelType

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
creds = Credentials(api_key)  # credentials object to access GENAI

# Instantiate parameters for text generation
params = GenerateParams(decoding_method="sample", max_new_tokens=10)

# Instantiate a model proxy object to send your requests
flan_ul2 = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

prompts = ["Hello! How are you?", "How's the weather?"]
for response in flan_ul2.generate_async(prompts):
    print(f"Prompt: {response.input_text}\nResponse: {response.generated_text}")
