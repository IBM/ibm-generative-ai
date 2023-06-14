import os
import time

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

print("\n------------- Example (Model Talk)-------------\n")

max_cycles = 20

bob_params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=25,
    min_new_tokens=1,
    stream=False,
    temperature=1,
    top_k=50,
    top_p=1,
)

alice_params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=45,
    min_new_tokens=1,
    stream=False,
    temperature=0,
    top_k=50,
    top_p=1,
)

creds = Credentials(api_key, api_endpoint)
bob_model = Model(ModelType.FLAN_UL2, params=bob_params, credentials=creds)
alice_model = Model(ModelType.FLAN_T5, params=alice_params, credentials=creds)

sentence = "Hello! How are you?"
print(f"[Alice] --> {sentence}")

for x in range(max_cycles):
    bob_response = bob_model.generate([sentence])
    # from first batch get first result generated text
    bob_gen = bob_response[0].generated_text
    print(f"[Bob] --> {bob_gen}")

    alice_response = alice_model.generate([bob_gen])
    # from first batch get first result generated text
    alice_gen = alice_response[0].generated_text
    print(f"[Alice] --> {alice_gen}")

    sentence = alice_gen
    time.sleep(1)
