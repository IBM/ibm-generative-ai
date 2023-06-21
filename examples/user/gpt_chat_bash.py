import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams, ModelType

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

print("\n------------- Example (GPT Chat)-------------\n")

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=128,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
)

creds = Credentials(api_key, api_endpoint)
chat = Model(ModelType.FLAN_UL2_20B, params=params, credentials=creds)


prompt = "Write a bash script to split string on comma display as list"
print(f"Prompt {prompt}")
responses = chat.generate([prompt])
for response in responses:
    print(f"Generated text:\n {response.generated_text}")
