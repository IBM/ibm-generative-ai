import os

from dotenv import load_dotenv

from genai.model import Credentials
from genai.schemas import PromptListParams
from genai.services.prompt_manager import PromptManager
from genai.services.prompt_saving import PromptSaving

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint=api_url)


print("\n------------- Example List Existing Prompt [ LIST ] -------------\n")
prompt_saving = PromptSaving(service_url=creds.api_endpoint, api_key=creds.api_key)
params = PromptListParams(limit=5, offset=0)
prompts = prompt_saving.list_prompts()
print(prompts.json())

prompts = PromptManager.list_prompts(creds=creds)
print(prompts)


print("\n------------- Example Prompt [ GET ONE ] -------------\n")
prompt_id = "dcfNVgGVUpW0gPr4"
prompt_saving = PromptSaving(service_url=creds.api_endpoint, api_key=creds.api_key)

prompts = prompt_saving.get_prompt(id=prompt_id)
print(prompts.json())

prompts = PromptManager.get_prompt(creds=creds, id=prompt_id)
print(prompts)
