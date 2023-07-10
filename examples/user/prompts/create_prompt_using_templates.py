import os

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.options import Options
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams
from genai.services.prompt_manager import PromptManager

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint=api_url)


watsonx_template = """
{{instruction}}

{{#list}}

Country: {{country}}
Capital: {{capital}}

{{/list}}
Country: {{input}}
"""

print("\n-------------  Create Mustaches Prompt Template [ SAVED TEMPLATE ] -------------\n")
prompt_templating = PromptPattern.from_watsonx(credentials=creds, name="QAPromptTemplate", template=watsonx_template)
print("\nSaved template information:\n", prompt_templating)


print("\n------------- Mustaches Prompt Template [ GET THE SAVED TEMPLATE ] -------------\n")
# If you save multiple templates with the same name, the first one will be returned by default (the most recent one)
# Otherwise you can specify the id of the template you want to retrieve
my_watsonx_prompt_template = PromptPattern.from_watsonx(credentials=creds, name="QAPromptTemplate")
print(my_watsonx_prompt_template.watsonx)

print("\n-------------  Creating Prompt using existing mustache template [ CREATE PROMPT ] -------------\n")

# prompt desing using existing watsonx template id
prompt_prototype = {
    "watsonx_template_id": my_watsonx_prompt_template.watsonx.id,
    "prompt_data": {
        "list": [
            {"country": "Canada", "capital": "Ottawa"},
            {"country": "Germany", "capital": "Berlin"},
            {"country": "USA", "capital": "Washington"},
        ]
    },
}

prompt = PromptManager.create_prompt(
    creds=creds,
    name="QACountryAirp",
    model_id="google/flan-ul2",
    prompt_prototype=prompt_prototype,
    input="Spain",
)
# NOTE: render prompt templating can be used here as well
print(prompt)

print("\n------------- Generate Response using saved prompt -------------\n")

params = GenerateParams(temperature=0.5)
model = Model(model="google/flan-ul2", params=params, credentials=creds)
options = Options(prompt_id=prompt.id)

responses = model.generate_as_completed(["Spain", "Finland", "Norway"], options=options)
for resp in responses:
    print(f"\nCountry: {resp.input_text} \n{resp.generated_text}")
