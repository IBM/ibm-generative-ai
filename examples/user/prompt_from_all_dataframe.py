import os
import pathlib

try:
    import pandas as pd
except ImportError:
    raise ImportError("Could not import pandas: Please install ibm-generative-ai[pandas] extension.")

from dotenv import load_dotenv

import genai.extensions.pandas  # noqa: F401
from genai.model import Credentials, Model
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams, ModelType

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
PATH = pathlib.Path(__file__).parent.resolve()

print("\n------------- Example (Pandas Dataframe Replacement)-------------\n")

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=15,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
    random_seed=2,
)

creds = Credentials(api_key)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

pt = PromptPattern.from_file(str(PATH) + os.sep + "templates" + os.sep + "synth-animal.yaml")
print("\nGiven template:\n", pt)

csv_path = str(PATH) + os.sep + "assets" + os.sep + "penguins2.csv"
df = pd.read_csv(csv_path, index_col=0)

mapping = {
    "species": ["species1", "species2", "species3"],
    "island": ["location1", "location2", "location3"],
    "flipper_length_mm": ["length1", "length2", "length3"],
    "year": ["dob1", "dob2", "dob3"],
}

list_of_prompts = pt.pandas.sub_all_from_dataframe(
    dataframe=df,
    col_to_var=mapping,
)

print("-----------------------")
print("generated prompt")
print(list_of_prompts)
print("Number of prompts: ", len(list_of_prompts))
print("-----------------------")

responses = model.generate_as_completed(list_of_prompts)
for response in responses:
    print(f"Generated text: {response.generated_text}")
