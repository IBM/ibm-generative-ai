"""
Tokenize text data

Runs tokenization asynchronously in parallel to achieve better performance
"""

from collections import Counter
from datetime import datetime

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import TextTokenizationParameters, TextTokenizationReturnOptions
from genai.text.tokenization import CreateExecutionOptions

try:
    from tqdm.auto import tqdm
except ImportError:
    print("Please install tqdm to run this example.")
    raise

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

greeting = "Hello! How are you?"
num_of_greetings = 10_000
lots_of_greetings = [greeting] * num_of_greetings

batch_size = 100
total_tokens = 0
token_frequency = Counter()

start_time = datetime.now()

print(heading("Running tokenization for many inputs in parallel"))
# yields batch of results that are produced asynchronously and in parallel
for response in tqdm(  # tqdm package can be used to show a progress bar during the tokenization
    client.text.tokenization.create(
        model_id="google/flan-t5-xl",
        input=lots_of_greetings,
        execution_options=CreateExecutionOptions(
            batch_size=batch_size,  # leave empty for optimal performance (specified for example purposes)
            ordered=False,  # responses arrive in unspecified order if False, use True to match the order of inputs.
        ),
        parameters=TextTokenizationParameters(
            return_options=TextTokenizationReturnOptions(
                tokens=True,  # return tokens
            )
        ),
    ),
    total=num_of_greetings // batch_size,
    unit="batch",
):
    for result in response.results:
        total_tokens += result.token_count
        token_frequency.update(result.tokens)

print(f"Total tokens: {total_tokens}")
print(f"Token frequency: {dict(token_frequency)}")
print(f"Time elapsed: {(datetime.now() - start_time).total_seconds():.2}s")
