"""
Moderate text data

Uncover HAP (hateful, abusive, profane language), Implicit hate or Stigma in text
"""

from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import (
    HAPOptions,
    SocialBiasOptions,
)
from genai.text.moderation import CreateExecutionOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

inputs = ["Ice cream sucks!", "It tastes like poop."]

print(heading("Run text moderation in parallel"))

for input_text, response in zip(
    inputs,
    client.text.moderation.create(
        inputs=inputs,
        hap=HAPOptions(threshold=0.5, send_tokens=True),
        social_bias=SocialBiasOptions(threshold=0.5, send_tokens=True),
        execution_options=CreateExecutionOptions(ordered=True),
    ),
):
    print(f"Input text: {input_text}")
    assert response.results
    result = response.results[0]

    # HAP
    assert result.hap
    hap = result.hap[0]
    print("HAP:")
    pprint(hap.model_dump())

    # Social Bias
    assert result.social_bias
    social_bias = result.social_bias[0]
    print("Social Bias:")
    pprint(social_bias.model_dump())

    print()
