"""
Enable/Disable logging for SDK

Follow the official logging documentation for more options:  https://docs.python.org/3/library/logging.config.html
"""

import logging

from dotenv import load_dotenv

from genai import Client, Credentials
from genai.schema import (
    DecodingMethod,
    TextGenerationParameters,
    TextGenerationReturnOptions,
)

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Most GEN-ai logs are at Debug level, so you can specifically enable
# or change the genai logging level here
logging.getLogger("genai").setLevel(logging.DEBUG)


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


print(heading("Generate text with detailed logs"))

client = Client(credentials=Credentials.from_env())
prompts = ["Hello! How are you?", "How's the weather?"]
for response in client.text.generation.create(
    model_id="google/flan-ul2",
    inputs=prompts,
    parameters=TextGenerationParameters(
        decoding_method=DecodingMethod.SAMPLE,
        max_new_tokens=10,
        return_options=TextGenerationReturnOptions(input_text=True),
    ),
):
    result = response.results[0]
    print(f"Prompt: {result.input_text}\nResponse: {result.generated_text}")
