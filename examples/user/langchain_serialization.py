import os
import tempfile

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams, ReturnOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
credentials = Credentials(api_key, api_endpoint)

llm = LangChainInterface(
    model="google/flan-ul2",
    credentials=credentials,
    params=GenerateParams(
        decoding_method="sample",
        max_new_tokens=10,
        min_new_tokens=1,
        stream=True,
        temperature=0.5,
        top_k=50,
        top_p=1,
        return_options=ReturnOptions(generated_tokens=True, token_logprobs=True, input_tokens=True),
    ),
)

with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
    print(f"Serializing LLM instance into '{tmp.name}'")
    llm.save(tmp.name)
    print(f"Loading serialized instance from '{tmp.name}'")
    llm_new = LangChainInterface.load_from_file(file=tmp.name, credentials=credentials)
    print("Comparing old instance with the new instance")
    assert llm == llm_new
    print(f"Done, removing '{tmp.name}'")
