import os

from dotenv import load_dotenv

from genai.model import Credentials

# from genai.services.prompt_manager import PromptManager
from genai.services.prompt_saving import PromptSaving

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint=api_url)


print("\n------------- Example Creating Prompt [ CREATE ] -------------\n")

template = {
    "data": {
        "example_file_ids": ["b83d8ba0-9c77-4df0-85d2-14a1e1769987"],
        # [
        #     {"country": "Canada", "capital": "Ottawa", "airport": "YOW"},
        #     {"country": "Germany", "capital": "Berlin", "airport": "BER"},
        #     {"country": "USA", "capital": "Washington", "airport": "DCA"}
        # ]
    }
}

prompt_saving = PromptSaving(service_url=creds.api_endpoint, api_key=creds.api_key)
prompt = prompt_saving.create_prompt(
    name="QACountryAirp", model_id="google/flan-t5-xl", template=template, input="Brazil"
)
print("\nPrompt created:\n", prompt)

# prompt = PromptManager.create_prompt(
# creds=creds, name="QACountryAirp", model_id="google/flan-t5-xl", template=template)
