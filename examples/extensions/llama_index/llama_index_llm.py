"""Use a model through LLamaIndex"""

from dotenv import load_dotenv
from llama_index.llms.base import ChatMessage
from llama_index.llms.types import MessageRole

from genai import Client
from genai.credentials import Credentials
from genai.extensions.llama_index import IBMGenAILlamaIndex
from genai.schema import DecodingMethod, TextGenerationParameters

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

llm = IBMGenAILlamaIndex(
    client=client,
    model_id="meta-llama/llama-2-70b-chat",
    parameters=TextGenerationParameters(
        decoding_method=DecodingMethod.SAMPLE,
        max_new_tokens=100,
        min_new_tokens=10,
        temperature=0.5,
        top_k=50,
        top_p=1,
    ),
)

print(heading("Complete text with llama index"))
prompt = "What is a molecule?"
print(f"Prompt: {prompt}")
result = llm.complete(prompt)
print(f"Answer: {result}")

print(heading("Chat with llama index"))
prompt = "Describe what is Python in one sentence."
print(f"Prompt: {prompt}")
message = llm.chat(
    messages=[
        ChatMessage(
            role=MessageRole.SYSTEM,
            content="You are a helpful, respectful and honest assistant.",
        ),
        ChatMessage(role=MessageRole.USER, content=prompt),
    ],
)
print(f'Answer: "{message}"')
