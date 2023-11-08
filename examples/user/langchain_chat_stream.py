import os

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainChatInterface
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)


llm = LangChainChatInterface(
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

prompt = "Describe what is Python in one sentence."
print(f"Request: {prompt}")
for chunk in llm.stream(
    input=[
        SystemMessage(
            content="""You are a helpful, respectful and honest assistant.
Always answer as helpfully as possible, while being safe.
Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.
Please ensure that your responses are socially unbiased and positive in nature. If a question does not make
any sense, or is not factually coherent, explain why instead of answering something incorrectly.
If you don't know the answer to a question, please don't share false information.
""",
        ),
        HumanMessage(content=prompt),
    ],
):
    print(f"Chunk Received:\n  Token: '{chunk.content}'\n  Info:{chunk.generation_info}")
