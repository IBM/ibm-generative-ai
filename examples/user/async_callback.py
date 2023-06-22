import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams, ModelType

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

print("\n------------- Example (Async Callback Greetings)-------------\n")

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=10,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
)

creds = Credentials(api_key, api_endpoint)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

greeting = "Hello! How are you?"
lots_of_greetings = [greeting] * 1000

# some global state for our call back
num_of_greetings = len(lots_of_greetings)
num_said_greetings = 0


# called for *when* a single input is complete in generate_async and not when
# generate returns next batch of results
def progress_callback(result):
    global num_of_greetings
    global num_said_greetings
    num_said_greetings += 1
    print(f"[Progress {str(float(num_said_greetings / num_of_greetings) * 100)}%]")
    try:
        print(f"\t {result.generated_text}")
    except Exception as e:
        print("Exception: result was = {} with exception = {}".format(result, str(e)))


# yields batch of results that are produced asynchronously and in parallel
for result in model.generate_async(lots_of_greetings, callback=progress_callback, hide_progressbar=True):
    pass
