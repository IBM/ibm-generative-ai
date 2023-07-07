import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.utils.search_space_params import grid_search_generate_params

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://workbench-api.res.ibm.com/v1"
load_dotenv()
API_KEY = os.getenv("GENAI_KEY", None)
API_ENDPOINT = os.getenv("GENAI_API", None)

print("\n------------- Example (String Replacement)-------------\n")

# use the dictionary to define the search space, keep the keys as
# the same from GenerateParams and use a list for the values to search
my_space_params = {
    "decoding_method": ["sample"],
    "max_new_tokens": [10, 20],
    "min_new_tokens": [1, 2],
    "temperature": [0.7, 0.8, 0.9, 1.5],
    "top_k": [50],
    "top_p": [1],
}

creds = Credentials(api_key=API_KEY, api_endpoint=API_ENDPOINT)

greeting1 = "Hello! How are you?"
greeting2 = "I am fine and you?"

# generate all combinations of parameters, returns a list of GenerateParams
generate_params_list = grid_search_generate_params(my_space_params)

for params in generate_params_list:
    model = Model("google/flan-ul2", params=params, credentials=creds)
    responses = model.generate_as_completed([greeting1, greeting2] * 4)

    print(f"Used params: \n{params} \n")

    print(greeting1)
    print(greeting2)
    for response in responses:
        print(f"Generated text: {response.generated_text}")
    print("------------------------------------")
