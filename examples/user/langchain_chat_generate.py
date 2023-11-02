import os

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage

from genai.credentials import Credentials
from genai.extensions.langchain.chat_llm import LangChainChatInterface
from genai.schemas import GenerateParams
from genai.schemas.generate_params import ChatOptions

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
result = llm.generate(
    messages=[
        [
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
        ]
    ],
)

conversation_id = result.generations[0][0].generation_info["meta"]["conversation_id"]
print(f"New conversation with ID '{conversation_id}' has been created!")
print(f"Response: {result.generations[0][0].text}")

prompt = "Show me some simple code example."
print(f"Request: {prompt}")
result = llm.generate(
    messages=[[HumanMessage(content=prompt)]],
    options=ChatOptions(conversation_id=conversation_id, use_conversation_parameters=True),
)
print(f"Response: {result.generations[0][0].text}")
