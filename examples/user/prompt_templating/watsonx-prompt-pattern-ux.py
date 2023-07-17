import os
import pathlib

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.options import Options
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
PATH = pathlib.Path(__file__).parent.resolve()

creds = Credentials(api_key, api_endpoint=api_url)
params = GenerateParams(temperature=0.5)

model = Model("google/flan-ul2", params=params, credentials=creds)


_template = """
{{instruction}}

{{#list}}

Country: {{country}}
Airport: {{airport}}
Capital: {{capital}}

{{/list}}
Country: {{input}}
"""

print("\n------------- Mustaches Prompt Template -------------\n")
pt = PromptPattern.from_watsonx(credentials=creds, name="list-qa-airport-3", template=_template)
print(f"\nPrompt: {pt}")


print("\n------------- Response -------------\n")
options = Options(
    watsonx_template=pt,
    watsonx_data={
        "instruction": "blaahh",
        "list": [
            {"country": "Canada", "capital": "Ottawa", "airport": "YOW"},
            {"country": "Germany", "capital": "Berlin", "airport": "BER"},
            {"country": "USA", "capital": "Washington", "airport": "DCA"},
        ],
    },
)


responses = model.generate_as_completed(["Spain", "Finland", "Iraq", "India", "Bangladesh"], options=options)
for resp in responses:
    print(f"\nCountry: {resp.input_text} \n{resp.generated_text}")
