import os

from dotenv import load_dotenv
from llama_index.llms import ChatMessage, MessageRole

from genai import Model
from genai.credentials import Credentials
from genai.extensions.llama_index import IBMGenAILlamaIndex
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)


model = Model(
    model="meta-llama/llama-2-70b-chat",
    credentials=Credentials(api_key, api_endpoint),
    params=GenerateParams(
        decoding_method="sample",
        max_new_tokens=100,
        min_new_tokens=10,
        temperature=0.5,
        top_k=50,
        top_p=1,
    ),
)
llm = IBMGenAILlamaIndex(model=model)

result = llm.complete("What is a molecule?")
print(f"Complete response: {result}")

prompt = "Describe what is Python in one sentence."
message = llm.chat(
    messages=[
        ChatMessage(
            role=MessageRole.SYSTEM,
            content="You are a helpful, respectful and honest assistant.",
        ),
        ChatMessage(role=MessageRole.USER, content=prompt),
    ],
)
print(f'Chat response: "{message}"')
