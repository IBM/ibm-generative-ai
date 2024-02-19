"""
Simple text generation
"""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import (
    TextGenerationParameters,
    TextGenerationReturnOptions,
)


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
client = Client(credentials=Credentials.from_env())

print(heading("Simple Text Generation"))
# yields batch of results that are produced asynchronously and in parallel
for response in client.text.generation.create(
    model_id="google/flan-t5-xl",
    inputs=["What is a molecule?", "What is NLP?"],
    parameters=TextGenerationParameters(
        max_new_tokens=150,
        min_new_tokens=20,
        return_options=TextGenerationReturnOptions(
            input_text=True,
        ),
    ),
):
    result = response.results[0]
    print(f"Input Text: {result.input_text}")
    print(f"Generated Text: {result.generated_text}")
    print("")
