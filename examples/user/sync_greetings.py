import os
import time

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import GenerateParams, ModelType

start_time = time.time()

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)

print("\n------------- Example (Sync Greetings)-------------\n")

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=10,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
)

creds = Credentials(api_key)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

greeting = "Hello! How are you?"
lots_of_greetings = [greeting] * 100
num_of_greetings = len(lots_of_greetings)
num_said_greetings = 0
greeting1 = "Hello! How are you?"


for result in model.generate_as_completed(lots_of_greetings):
    num_said_greetings += 1
    print(f"[Progress {str(float(num_said_greetings/num_of_greetings)*100)}%]")
    if result is not None:
        print(f"\t {result.generated_text}")
    else:
        print("\t <the result was 'None' for this input>")

print("--- %s seconds ---" % (time.time() - start_time))
