import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)

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


print("\n------------- Rendered Prompt -------------\n")
inputs = ["Spain", "Finland", "Iraq", "India", "Bangladesh"]
data = {
    "list": [
        {"country": "Canada", "capital": "Ottawa", "airport": "YOW"},
        {"country": "Germany", "capital": "Berlin", "airport": "BER"},
        {"country": "USA", "capital": "Washington", "airport": "DCA"},
    ]
}

rendered_prompts = pt.render(inputs=inputs, data=data)
for pt in rendered_prompts:
    print(pt)
    print("- - - - ")
