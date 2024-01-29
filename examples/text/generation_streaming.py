"""Stream answer from a model"""

import sys
from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import (
    DecodingMethod,
    ModerationHAP,
    ModerationParameters,
    TextGenerationParameters,
    TextGenerationReturnOptions,
    TextModeration,
)

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


# Instantiate a model proxy object to send your requests
client = Client(credentials=Credentials.from_env())


model_id = "meta-llama/llama-2-70b"
prompt = "The gesture of a hand with pinched fingers 🤌 is actually rude in Italy. "
parameters = TextGenerationParameters(
    decoding_method=DecodingMethod.SAMPLE,
    max_new_tokens=90,
    min_new_tokens=50,
    return_options=TextGenerationReturnOptions(generated_tokens=True),
    temperature=0.1,
    repetition_penalty=1.5,
    random_seed=3293482354,
)
moderations = ModerationParameters(
    hap=ModerationHAP(input=False, output=True, send_tokens=True, threshold=0.5),
    # possibly add more moderations:
    # implicit_hate=ModerationImplicitHate(...),
    # stigma=ModerationStigma(...),
)
hate_speach_in_output: list[TextModeration] = []


print(heading("Generating text stream"))

print(prompt, end="")
for response in client.text.generation.create_stream(
    model_id=model_id, input=prompt, parameters=parameters, moderations=moderations
):
    if not response.results:
        hate_speach_in_output.extend(response.moderation.hap)
        continue
    for result in response.results:
        if result.generated_text:
            print(result.generated_text, end="")

print()
print(heading("Hate speach in output"), file=sys.stderr)
pprint([hap.model_dump() for hap in hate_speach_in_output], stream=sys.stderr)
