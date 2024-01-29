"""
Working with system prompts

The system prompt is a pre-defined prompt that helps cue the model to exhibit the desired behavior for a specific task.
"""

from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
client = Client(credentials=Credentials.from_env())


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


print(heading("Create a system prompt"))
prompt_name = "Simple Verbalizer"
prompt_content = """classify { "label 1", "label 2" } Input: {{input}} Output:"""
create_response = client.system_prompt.create(name=prompt_name, content=prompt_content)
system_prompt_id = create_response.result.id
print(f"System Prompt ID: {system_prompt_id}")

print(heading("Get a system prompt details"))
retrieve_response = client.system_prompt.retrieve(id=system_prompt_id)
pprint(retrieve_response.result.model_dump())

print(heading("Show all existing system prompts"))
system_prompt_list_response = client.system_prompt.list(offset=0, limit=10)
print("Total Count: ", system_prompt_list_response.total_count)
print("Results: ", system_prompt_list_response.results)

print(heading("Delete a system prompt"))
client.system_prompt.delete(id=system_prompt_id)
print("OK")
