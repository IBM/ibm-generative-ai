import inspect
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

print("\n------------- Example (Complete my code)-------------\n")

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=5,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
)

creds = Credentials(api_key, api_endpoint)
code_explainer = Model(ModelType.CODEGEN_MONO_16B, params=params, credentials=creds)


# pass in an actual python function to explain
def add_numbers(number_one, number_two):
    return number_one


prompt = inspect.getsource(add_numbers)
print(prompt + "\n")
responses = code_explainer.generate([prompt])
for response in responses:
    print(f"Generated text:\n {response.generated_text}")
