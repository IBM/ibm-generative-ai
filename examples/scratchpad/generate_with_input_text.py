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
creds = Credentials(api_key, api_endpoint)  # credentials object to access GENAI

# Instantiate parameters for text generation
params = GenerateParams(decoding_method="sample", max_new_tokens=100)

# Instantiate a model proxy object to send your requests
flan_ul2 = Model(ModelType.FLAN_T5_11B, params=params, credentials=creds)

prompt = "Question: For his 30th birthday, Elvira chose a new computer with many \
    accessories as a gift. She has a budget of €1500 donated by her whole family and \
    thinks that she will be able to keep a little money to afford a garment. She \
    goes to a computer store and chooses a machine that costs €1090 with a screen, \
    keyboard and mouse. She also takes a scanner for €157, a CD burner worth €74 \
    and a printer for €102. How much money will she have left for her clothing?"


prompts = [prompt]
for response in flan_ul2.generate_async(prompts):
    print(f"Prompt: {response.input_text}\nResponse: {response.generated_text}")
