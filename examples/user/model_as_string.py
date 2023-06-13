import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint)  # credentials object to access GENAI

# Instantiate parameters for text generation
params = GenerateParams(decoding_method="sample", max_new_tokens=10)

# model object
flan = Model("google/flan-ul2", params=params, credentials=creds)
ul2 = Model("google/ul2", params=params, credentials=creds)
t5 = Model("prakharz/dial-flant5-xl", params=params, credentials=creds)

# Q&A with flan-ul2
print("\n------------- Example (Input flan-ul2 model as string)-------------\n")
prompts = ["What is your name?", "Where are you from?"]
for response in flan.generate_async(prompts):
    print(f"Prompt: {response.input_text}\nResponse: {response.generated_text}")

# Q&A with ul2
print("\n------------- Example (Input ul2 model as string)-------------\n")
for response in ul2.generate_async(prompts):
    print(f"Prompt: {response.input_text}\nResponse: {response.generated_text}")

# Q&A with gpt
print("\n------------- Example (Input t5-xl model as string)-------------\n")
for response in t5.generate_async(prompts):
    print(f"Prompt: {response.input_text}\nResponse: {response.generated_text}")
