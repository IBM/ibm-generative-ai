import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams
from genai.schemas.generate_params import HAPOptions, ModerationsOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint)  # credentials object to access GENAI

# Instantiate parameters for text generation
params = GenerateParams(
    decoding_method="sample",
    min_new_tokens=10,
    max_new_tokens=20,
    stream=True,
    moderations=ModerationsOptions(
        # Threshold is set to very low level to flag everything (testing purposes)
        # or set to True to enable HAP with default settings
        hap=HAPOptions(input=True, output=True, threshold=0.01)
    ),
)

# Instantiate a model proxy object to send your requests
flan_ul2 = Model("google/flan-ul2", params=params, credentials=creds)

prompts = ["Hello world!"]
for response in flan_ul2.generate_stream(prompts):
    print(f"Response: {response.generated_text}")
    print(f"Moderation: {response.moderation}")
    print("======")
