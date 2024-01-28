"""
Compare a set of hyperparameters

Run a grid search over all possible combinations of parameters
"""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import (
    DecodingMethod,
    TextGenerationComparisonCreateRequestRequest,
    TextGenerationComparisonParameters,
    TextGenerationParameters,
)

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

prompt = "The capital of Madrid is Spain. The capital of Canada is"

print(heading("Run text generation with many parameter combinations"))
response = client.text.generation.compare(
    request=TextGenerationComparisonCreateRequestRequest(
        model_id="google/flan-t5-xxl",
        parameters=TextGenerationParameters(min_new_tokens=1, max_new_tokens=10, decoding_method=DecodingMethod.SAMPLE),
        input=prompt,
    ),
    # Grid search through all possible combinations of the following parameters:
    compare_parameters=TextGenerationComparisonParameters(
        top_k=[10, 50],
        repetition_penalty=[1.0, 1.5],
        temperature=[0.7, 0.9, 1.5, 2.0],
    ),
)

print(f"Prompt: {prompt}\n")

for params_combination in response.results:
    print(f"Used params: {params_combination.parameters.model_dump()}")
    assert params_combination.result
    print(f"Generated text: {params_combination.result.results[0].generated_text}\n")
