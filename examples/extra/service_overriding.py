"""
Overriding built-in services

If you want to override or extend the behaviour of some service, you can do so by providing your own class.
Generally, you can achieve it by supplying your service on the local level (preferred) or global level.
"""

from dotenv import load_dotenv

from genai import ApiClient, Client, Credentials
from genai.text import TextService
from genai.text.generation import GenerationService as OriginalGenerationService

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def local_approach(api_client: ApiClient):
    """Locally override services (preferred)"""

    class MyGenerationService(OriginalGenerationService):
        def my_custom_method(self):
            return "Greeting!"

    class TextServiceServices(TextService.Services):
        GenerationService: type[OriginalGenerationService] = MyGenerationService

    class MyTextService(TextService):
        Services = TextServiceServices

    client = Client(api_client=api_client, services=Client.Services(TextService=MyTextService))
    client.text.generation.my_custom_method()


def global_approach(api_client: ApiClient):
    """Globally override services (non preferred)"""

    class MyGenerationService(OriginalGenerationService):
        def my_custom_method(self):
            pass

    class MyTextService(TextService.Services):
        GenerationService: type[OriginalGenerationService] = MyGenerationService

    TextService.Services = MyTextService

    client = Client(api_client=api_client)
    client.text.generation.my_custom_method()


credentials = Credentials.from_env()
api_client = ApiClient(credentials=credentials)

local_approach(api_client)
global_approach(api_client)
