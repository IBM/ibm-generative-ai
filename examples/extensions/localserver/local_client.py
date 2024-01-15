"""Customize behavior of local client"""

from typing import Generator

from dotenv import load_dotenv

from genai import Client, Credentials
from genai.client import BaseServices as ClientServices
from genai.text.generation import TextGenerationCreateResponse
from genai.text.generation.generation_service import GenerationService
from genai.text.text_service import TextService

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


class LocalGenerationService(GenerationService):
    def create(self, **kwargs) -> Generator[TextGenerationCreateResponse, None, None]:
        for response in super().create(**kwargs):
            response.results[0].generated_text = "You've been hacked!"
            yield response


class LocalTextService(TextService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, services=TextService.Services(GenerationService=LocalGenerationService))


class LocalClient(Client):
    def __init__(self, credentials: Credentials):
        super().__init__(credentials=credentials, services=ClientServices(TextService=LocalTextService))


print(heading("Use custom text service implementation"))

# Instantiate a custom client
client = LocalClient(credentials=Credentials.from_env())
for response in client.text.generation.create(model_id="google/flan-t5-xl", inputs="aha!"):
    for result in response.results:
        print(result.generated_text)
