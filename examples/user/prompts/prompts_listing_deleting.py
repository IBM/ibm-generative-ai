import os

from dotenv import load_dotenv

from genai.model import Credentials
from genai.services.prompt_manager import PromptManager

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint=api_url)

print("\n------------- Example List Existing Prompt [ LIST ] -------------\n")

prompts = PromptManager.list_prompts(creds=creds)
for pt in prompts.results:
    print(pt, "\n")


print("\n------------- Example Prompt [ GET ONE ] -------------\n")
prompt_id = prompts.results[0].id
selected_prompt = PromptManager.get_prompt(creds=creds, id=prompt_id)
print(selected_prompt)

print("\n------------- Example Deleting [ DELETE ONE ] -------------\n")
prompt_id = selected_prompt.id
prompt_delete = PromptManager.delete_prompt(creds=creds, id=prompt_id)
print(prompt_delete)
