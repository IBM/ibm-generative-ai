"""
Customize HTTP communication options ('httpx' library settings)

For example provide TLS certificates / modify timeout
"""

import logging

from dotenv import load_dotenv

from genai import Client, Credentials
from genai.text.generation import DecodingMethod, TextGenerationParameters

logging.basicConfig(level="ERROR")

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


print(heading("Generate text with custom http communication"))


config = {
    "api_client_config": {
        # Allow up to 2 retries, disable SSL verification
        "transport_options": {"retries": 2, "verify": False},
        # Disable SSL verification, set general timeout to 10 seconds with specific timeout for establishing connection
        "client_options": {"verify": False, "timeout": {"timeout": 10, "connect": 3}},
    }
}
client = Client(credentials=Credentials.from_env(), config=config)

responses = list(
    client.text.generation.create(
        model_id="google/flan-ul2",
        inputs=["Generate a random number"],
        parameters=TextGenerationParameters(decoding_method=DecodingMethod.SAMPLE, max_new_tokens=5, min_new_tokens=1),
    )
)
print(f"Your random number is: {responses[0].results[0].generated_text}")
