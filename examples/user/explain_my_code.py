import inspect
import os

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import GenerateParams, ModelType

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)

print("\n------------- Example (Explain my code)-------------\n")

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=50,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
)

creds = Credentials(api_key)
code_explainer = Model(ModelType.CODEGEN_MONO_16B, params=params, credentials=creds)


# pass in an actual python function to explain
def add_numbers(number_one, number_two):
    return number_one + number_two


prompt = inspect.getsource(add_numbers) + "# Explanation of what the code does"
print(prompt + "\n")
responses = code_explainer.generate([prompt])
for response in responses:
    print(f"Generated text:\n {response.generated_text}")
