import os

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import GenerateParams, ModelType, ReturnOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)

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

creds = Credentials(api_key)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

# load a prompt from file
with open("prompts/Country-Capital-Factual-QA", "r") as f:
    prompt = f.read()

print(f"Prompt: \n {prompt}\n")

# Call generate function
responses = model.generate_as_completed([prompt])
for response in responses:
    print(f"Generated text: {response.generated_text}")
