import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams
from genai.schemas.chat import HumanMessage, SystemMessage
from genai.schemas.generate_params import ChatOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY")
api_endpoint = os.getenv("GENAI_API")

print("\n------------- Example (Chat)-------------\n")

params = GenerateParams(
    decoding_method="sample", max_new_tokens=128, min_new_tokens=30, temperature=0.7, top_k=50, top_p=1
)

creds = Credentials(api_key, api_endpoint)
model = Model("meta-llama/llama-2-70b-chat", params=params, credentials=creds)

prompt = "What is NLP and how it has evolved over the years?"
response = model.chat(
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
)
print(f"Conversation ID: {response.conversation_id}")
print(f"Request: {prompt}")
print(f"Response: {response.results[0].generated_text}")

prompt = "How can I start?"
response = model.chat(
    [
        HumanMessage(content=prompt),
    ],
    options=ChatOptions(
        conversation_id=response.conversation_id,
        use_conversation_parameters=True,
    ),
)
print(f"Request: {prompt}")
print(f"Response: {response.results[0].generated_text}")
