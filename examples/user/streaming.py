import os

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import GenerateParams, ModelType, ReturnOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
creds = Credentials(api_key=api_key)

print("\n------------- Example (Explain my code)-------------\n")

# Instantiate parameters for text generation
params = GenerateParams(
    decoding_method="sample", max_new_tokens=500, min_new_tokens=10, return_options=ReturnOptions(generated_tokens=True)
)

# Instantiate a model proxy object to send your requests
flan_ul2 = Model(ModelType.FLAN_UL2_20B, params=params, credentials=creds)

prompts = [" Explain life in one sentence"]
count = 0

for response in flan_ul2.generate_stream(prompts):
    print(response.input_token_count) if count == 0 else print(response.generated_text)
    count = count + 1
