import os
import pathlib

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams

#
# In this demo, the following dataset was used:
#
# Gorman KB, Williams TD, Fraser WR (2014) "Ecological Sexual Dimorphism and Environmental Variability within a Community of Antarctic Penguins (Genus Pygoscelis)." PLoS ONE 9(3): e90081. doi:10.1371/journal.pone.0090081  # noqa

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
PATH = pathlib.Path(__file__).parent.resolve()

print("\n------------- Example (String Replacement)-------------\n")

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=15,
    min_new_tokens=1,
    stream=False,
)

creds = Credentials(api_key, api_endpoint)
model = Model("google/flan-ul2", params=params, credentials=creds)


prompt = PromptPattern.from_file(str(PATH) + os.sep + "templates" + os.sep + "synth-animal.yaml")
print("\nGiven template:\n", prompt)

prompt.sub("animal", "penguins")
csv_path = str(PATH) + os.sep + "assets" + os.sep + "penguins.csv"
mapping = {
    "species": ["species1", "species2", "species3"],
    "island": ["location1", "location2", "location3"],
    "flipper_length_mm": ["length1", "length2", "length3"],
    "year": ["dob1", "dob2", "dob3"],
}

list_of_prompts = prompt.sub_all_from_csv(
    csv_path=csv_path,
    col_to_var=mapping,
)

print("-----------------------")
print("generated prompt")
print(list_of_prompts)
print(len(list_of_prompts))
print("-----------------------")


responses = model.generate_as_completed(list_of_prompts)
for response in responses:
    print(f"Generated text: {response.generated_text}")
