import logging
import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams, ModelType, TokenParams

logging.getLogger("genai").setLevel(logging.INFO)


# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
creds = Credentials(api_key=api_key, api_endpoint=api_endpoint)  # credentials object to access GENAI


# Instantiate parameters for text generation
generate_params = GenerateParams(decoding_method="sample", max_new_tokens=500, min_new_tokens=10)
tokenize_params = TokenParams(return_tokens=True)


flan_ul2 = Model(ModelType.FLAN_UL2_20B, params=generate_params, credentials=creds)
prompts = ["Explain life in one sentence:", "Write a python function to permute an array."] * 5
print("======== Async Generate (responses need not be in order) ======== ")
counter = 0
for response in flan_ul2.generate_async(prompts):
    counter += 1
    if response is not None:
        print(counter, response.input_text, " --> ", response.generated_text)
    else:
        print(counter, ":", None)

print("======== Async Generate with ordered=True (responses in order) ======== ")
counter = 0
for response in flan_ul2.generate_async(prompts, ordered=True):
    counter += 1
    if response is not None:
        print(
            counter,
            ": Input Prompt ==> ",
            prompts[counter - 1],
            "\n(Input text, Generated text) ==>",
            response.input_text,
            " --> ",
            response.generated_text,
        )
    else:
        print(counter, ":", None)


# Instantiate a model proxy object to send your requests
flan_ul2 = Model(ModelType.FLAN_UL2_20B, params=tokenize_params, credentials=creds)
prompts = ["Explain life in one sentence:", "Write a python function to permute an array." * 5] * 5
print("======== Async Tokenize (responses need not be in order) ======== ")
counter = 0
for response in flan_ul2.tokenize_async(prompts):
    counter += 1
    if response is not None:
        print(counter, ":", response.input_text, " --> ", response.tokens)
    else:
        print(counter, ":", None)

print("======== Async Tokenize with ordered=True (responses in order) ======== ")
counter = 0
for response in flan_ul2.tokenize_async(prompts, ordered=True):
    counter += 1
    if response is not None:
        print(
            counter,
            ": Input Prompt ==>",
            prompts[counter - 1],
            "\n(Input text, Tokens) ==>",
            response.input_text,
            " --> ",
            response.tokens,
        )
    else:
        print(counter, ":", None)
