import os
import pathlib

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams, ModelType

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
PATH = pathlib.Path(__file__).parent.resolve()

print("\n------------- Example (Greetings)-------------\n")

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

# can live locally or at an url endpoint
pt = PromptPattern.from_file(str(PATH) + os.sep + "templates" + os.sep + "capital-qa.yaml")
pt.sub("country", "Spain")
print(pt)
responses = model.generate_as_completed([str(pt)])
for response in responses:
    print(f"Generated text: {response.generated_text}")
