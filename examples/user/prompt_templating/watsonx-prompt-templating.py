import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.prompt_pattern import PromptPattern
from genai.schemas import TokenParams
from genai.services.prompt_template_manager import PromptTemplateManager

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)

print("\n------------- Example Mustaches Prompt [ CREATE ] -------------\n")

params = TokenParams(return_tokens=True)

creds = Credentials(api_key, api_endpoint=api_url)

_template = """
{{ instruction }}
{{#examples}}

{{input}}
{{output}}

{{/examples}}
{{input}}
"""

print("\n------------- Example Mustaches Prompt [ SAVE ] -------------\n")
test_pt = PromptPattern.from_watsonx(credentials=creds, name="test", template=_template)
print("\nSaved template information:\n", test_pt)


print("\n------------- Example Mustaches Prompt [ LIST ] -------------\n")
pts = PromptTemplateManager.load_all_templates(credentials=creds)
for r in pts.results:
    print(f"{r.name}, {r.id}")


print("\n------------- Example Mustaches Prompt [ GET ONE ] -------------\n")
template = PromptPattern.from_watsonx(credentials=creds, name="aa", template=_template)
print(template.watsonx)


print("\n------------- Example Mustaches Prompt [ UPDATE ] -------------\n")
template = PromptPattern.from_watsonx(credentials=creds, name="aa", template="{{a}}{{b}}")
print(template.watsonx)


print("\n------------- Example Mustaches Prompt [ DELETE ] -------------\n")
_id = test_pt.delete()
print(f"\n Deleted prompt with id : {_id}")
