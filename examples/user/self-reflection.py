import os
import pathlib

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams, ModelType

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
PATH = pathlib.Path(__file__).parent.resolve()

print("\n------------- Example (PromptPatterns) -------------\n")

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=20,
    min_new_tokens=1,
    stream=False,
)

creds = Credentials(api_key, api_endpoint)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

# (1) Prompt
prompt = "Is McDonald's or Burger King better?"

print("INPUT>> " + prompt + "\n")
responses = model.generate([prompt])
gen_response = responses[0].generated_text.strip()

# (2) Internal monolog
print("[Internal monologue]")
print(f"[My answer]: {gen_response}")

# (2.1) critic myself with template
pt = PromptPattern.from_file(str(PATH) + os.sep + "templates" + os.sep + "self-reflection.yaml")
pt.sub("prompt", prompt)
pt.sub("response", gen_response)
print(f"[Self reflection]: {pt}")

# (2.2) critic my answer
# adjust params
params.min_new_tokens = 1
params.max_new_tokens = 1
responses = model.generate([pt])
gen_control_ans = responses[0].generated_text
print(f"[Self reflection answer]: {gen_control_ans}" + "\n")

# (3) self-control flow
if "yes" in gen_control_ans.lower():
    print("<< Sorry I should not comment.")
else:
    print("<<OUTPUT " + gen_response)
