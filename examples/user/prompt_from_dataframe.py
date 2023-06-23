import os
import pathlib

try:
    import pandas as pd
except ImportError:
    raise ImportError("Could not import pandas: Please install ibm-generative-ai[pandas] extension.")

from dotenv import load_dotenv

import genai.extensions.pandas  # noqa: F401
from genai.credentials import Credentials
from genai.model import Model
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams, ModelType

#
# In this demo, the following dataset was used:
#
# Gorman KB, Williams TD, Fraser WR (2014) "Ecological Sexual Dimorphism and Environmental Variability within a Community of Antarctic Penguins (Genus Pygoscelis)." PLoS ONE 9(3): e90081. doi:10.1371/journal.pone.0090081 # noqa

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
PATH = pathlib.Path(__file__).parent.resolve()

print("\n------------- Example (Pandas Dataframe Replacement)-------------\n")

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=15,
    min_new_tokens=1,
    stream=False,
)

creds = Credentials(api_key, api_endpoint)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)


csv_path = str(PATH) + os.sep + "assets" + os.sep + "penguins.csv"
df = pd.read_csv(csv_path, index_col=0)

pt = PromptPattern.from_str("{{species}}: {{island}}, {{flipper_length_mm}}, {{year}}\n")
list_of_prompts = pt.pandas.sub_from_dataframe(dataframe=df, start_index=15, n=2, strategy="sample")

print("-----------------------")
print("generated prompt")
print(list_of_prompts)
print("Number of prompts: ", len(list_of_prompts))
print("-----------------------")

responses = model.generate_as_completed(list_of_prompts)
for response in responses:
    print(f"Generated text: {response.generated_text}")
