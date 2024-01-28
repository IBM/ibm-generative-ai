"""
Create a custom prompt with variables
"""

from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import DecodingMethod, LengthPenalty, TextGenerationParameters, TextGenerationReturnOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
client = Client(credentials=Credentials.from_env())


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


prompt_name = "My prompt"
model_id = "google/flan-t5-xl"

print(heading("Create prompt"))
template = "This is the recipe for {{meal}} as written by {{author}}: "
create_response = client.prompt.create(
    model_id=model_id,
    name=prompt_name,
    input=template,
    data={"meal": "goulash", "author": "Shakespeare"},
    parameters=TextGenerationParameters(
        length_penalty=LengthPenalty(decay_factor=1.5),
        decoding_method=DecodingMethod.SAMPLE,
    ),
)
prompt_id = create_response.result.id
print(f"Prompt id: {prompt_id}")

print(heading("Get prompt details"))
retrieve_response = client.prompt.retrieve(id=prompt_id)
pprint(retrieve_response.result.model_dump())

print(heading("Generate text using prompt"))
[generation_response] = list(
    client.text.generation.create(
        prompt_id=prompt_id,
        parameters=TextGenerationParameters(return_options=TextGenerationReturnOptions(input_text=True)),
    )
)
[result] = generation_response.results
print(f"Prompt: {result.input_text}")
print(f"Answer: {result.generated_text}")

print(heading("Override prompt template variables"))
[generation_response] = list(
    client.text.generation.create(
        prompt_id=prompt_id,
        parameters=TextGenerationParameters(return_options=TextGenerationReturnOptions(input_text=True)),
        data={"meal": "pancakes", "author": "Edgar Allan Poe"},
    )
)
[result] = generation_response.results
print(f"Prompt: {result.input_text}")
print(f"Answer: {result.generated_text}")

print(heading("Show all existing prompts"))
prompt_list_response = client.prompt.list(search=prompt_name, limit=10, offset=0)
print("Total Count: ", prompt_list_response.total_count)
print("Results: ", prompt_list_response.results)

print(heading("Delete prompt"))
client.prompt.delete(id=prompt_id)
print("OK")
