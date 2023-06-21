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

print("\n------------- Example (String Replacement)-------------\n")

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=1000,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
    random_seed=2,
)

creds = Credentials(api_key, api_endpoint)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)


# load prompt pattern from file
pt = PromptPattern.from_file(str(PATH) + os.sep + "templates" + os.sep + "instruction.yaml")
print("\nGiven template:\n", pt)

json_path = str(PATH) + os.sep + "assets" + os.sep + "seed_tasks.jsonl"
mapping = {
    "instruction": ["instruction1", "instruction2", "instruction3", "instruction4", "instruction5"],
    "input": ["input1", "input2", "input3", "input4", "input5"],
    "output": ["output1", "output2", "output3", "output4", "output5"],
}

# Build multiple prompt template using all available data from json
list_of_prompts = pt.sub_all_from_json(json_path=json_path, key_to_var=mapping)

# Build 'n' multiple prompt template using available data from json
list_of_prompts = pt.sub_from_json(json_path=json_path, key_to_var=mapping, strategy="sample", n=4)

print("-----------------------")
print("generated prompt")
print(list_of_prompts)
print("-----------------------")


responses = model.generate_as_completed(list_of_prompts)
for response in responses:
    print(f"Generated text: {response.generated_text}")
