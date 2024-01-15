"""Serialize LangChain model to a file"""

import tempfile

from dotenv import load_dotenv

from genai import Client, Credentials
from genai.extensions.langchain import LangChainInterface
from genai.text.generation import (
    DecodingMethod,
    TextGenerationParameters,
    TextGenerationReturnOptions,
)

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

print(heading("Serialize a langchain chain"))

llm = LangChainInterface(
    model_id="google/flan-ul2",
    client=client,
    parameters=TextGenerationParameters(
        decoding_method=DecodingMethod.SAMPLE,
        max_new_tokens=10,
        min_new_tokens=1,
        temperature=0.5,
        top_k=50,
        top_p=1,
        return_options=TextGenerationReturnOptions(generated_tokens=True, token_logprobs=True, input_tokens=True),
    ),
)

with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
    print(f"Serializing LLM instance into '{tmp.name}'")
    llm.save(tmp.name)
    print(f"Loading serialized instance from '{tmp.name}'")
    llm_new = LangChainInterface.load_from_file(file=tmp.name, client=client)
    print("Comparing old instance with the new instance")
    assert llm == llm_new
    print(f"Done, removing '{tmp.name}'")
