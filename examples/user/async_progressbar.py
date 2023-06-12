import os

from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import GenerateParams, ModelType

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)

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

creds = Credentials(api_key)
model = Model(ModelType.FLAN_UL2, params=params, credentials=creds)

greeting = "Hello! How are you?"
lots_of_greetings = [greeting] * 100

# By default *hide_progressbar* parameter is False.
# If you want to hide the progress bar pass *hide_progressbar=True* to *generate_async*.
for result in model.generate_async(lots_of_greetings):
    pass
