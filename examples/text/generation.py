"""
Complex text generation example with a progress bar

Runs text generation asynchronously in parallel to achieve better performance
"""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import (
    DecodingMethod,
    LengthPenalty,
    ModerationParameters,
    ModerationStigma,
    TextGenerationParameters,
    TextGenerationReturnOptions,
)
from genai.text.generation import CreateExecutionOptions

try:
    from tqdm.auto import tqdm
except ImportError:
    print("Please install tqdm to run this example.")
    raise


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
client = Client(credentials=Credentials.from_env())

greeting = "Hello! How are you?"
lots_of_greetings = [greeting] * 20

moderations = ModerationParameters(
    stigma=ModerationStigma(input=False, threshold=0.8),
    # possibly add more moderations:
    # implicit_hate=ModerationImplicitHate(...),
    # hap=ModerationHAP(...),
)

parameters = TextGenerationParameters(
    max_new_tokens=10,
    decoding_method=DecodingMethod.SAMPLE,
    length_penalty=LengthPenalty(start_index=5, decay_factor=1.5),
    return_options=TextGenerationReturnOptions(
        # if ordered is False, you can use return_options to retrieve the corresponding prompt
        input_text=True,
    ),
)

print(heading("Generating responses in parallel"))
# yields batch of results that are produced asynchronously and in parallel
for idx, response in tqdm(
    enumerate(
        client.text.generation.create(
            model_id="google/flan-t5-xl",
            inputs=lots_of_greetings,
            moderations=moderations,
            # set to ordered to True if you need results in the same order as prompts
            execution_options=CreateExecutionOptions(ordered=False),
            parameters=parameters,
        )
    ),
    total=len(lots_of_greetings),
    desc="Progress",
    unit="input",
):
    result = response.results[0]
    print(f"Input text ({idx}): {result.input_text}")
    print(f"Generated text ({idx}): {result.generated_text}")
