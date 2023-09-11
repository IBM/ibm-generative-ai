import logging
import os

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import GenerateParams
from genai.utils.http_provider import HttpProvider

logging.basicConfig(level="ERROR")

# Modify options for `httpx` library which the SDK uses
HttpProvider.default_http_client_options["verify"] = False
HttpProvider.default_http_transport_options["verify"] = False

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key=api_key, api_endpoint=api_url)


# Instantiate parameters for text generation
generate_params = GenerateParams(decoding_method="sample", max_new_tokens=5, min_new_tokens=1)
flan_ul2 = Model("google/flan-ul2", params=generate_params, credentials=creds)
[response] = flan_ul2.generate(prompts=["Generate a random number"])
print(f"Your random number is: {response.generated_text}")
