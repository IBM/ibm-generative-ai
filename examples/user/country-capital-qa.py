import os
import pathlib

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams, ModelType, ReturnOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

print("\n------------- Example (Country-Capital-Factual-QA)-------------\n")

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=1,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
    return_options=ReturnOptions(input_text=False, input_tokens=True),
)

creds = Credentials(api_key, api_endpoint)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

prompt_path = pathlib.Path(__file__, "..", "prompts", "Country-Capital-Factual-QA").resolve()
print(prompt_path)
# load a prompt from file
with open(prompt_path, "r") as f:
    prompt = f.read()

print(f"Prompt: \n {prompt}\n")

# Call generate function
responses = model.generate_as_completed([prompt])
for response in responses:
    print(f"Generated text: {response.generated_text}")
