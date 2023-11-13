import os

from dotenv import load_dotenv
from llama_index.llms import LangChainLLM

from genai import Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams

load_dotenv()
api_key = os.environ.get("GENAI_KEY")
api_url = os.environ.get("GENAI_API")
langchain_model = LangChainInterface(
    model="meta-llama/llama-2-70b-chat",
    credentials=Credentials(api_key, api_endpoint=api_url),
    params=GenerateParams(
        decoding_method="sample",
        min_new_tokens=1,
        max_new_tokens=10,
    ),
)

llm = LangChainLLM(llm=langchain_model)
response_gen = llm.stream_chat("What is a molecule?")
for delta in response_gen:
    print(delta.delta)
