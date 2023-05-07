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
prompts = ["Hello! How are you?", "How's the weather?"]

print(
    "==== Note that enum with symbols mapping to the same"
    " value does not yield to iterating over all the unique symbols,"
    " rather it represents all the symbols mapping to a single value"
    " by a single symbol during iteration. For example, if there are"
    " three symbols symb1, symb2, symb3 mapping to one value then"
    " during iteration it will do symb1 symb1 symb1 due to how it"
    " maps internally. ===="
)
for key, modelid in ModelType.__members__.items():
    model = Model(modelid, params=params, credentials=creds)
    responses = [response.generated_text for response in model.generate(prompts)]
    print(modelid, ":", responses)
    model = Model(modelid.value, params=params, credentials=creds)
    responses = [response.generated_text for response in model.generate(prompts)]
    print(modelid.value, ":", responses)
