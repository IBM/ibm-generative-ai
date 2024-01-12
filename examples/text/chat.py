"""Chat with a model"""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.text.chat import HumanMessage, SystemMessage
from genai.text.generation import DecodingMethod, TextGenerationParameters

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


params = TextGenerationParameters(
    decoding_method=DecodingMethod.SAMPLE, max_new_tokens=128, min_new_tokens=30, temperature=0.7, top_k=50, top_p=1
)

client = Client(credentials=Credentials.from_env())
model_id = "meta-llama/llama-2-70b-chat"

prompt = "What is NLP and how it has evolved over the years?"
print(heading("Generating a chat response"))
response = client.text.chat.create(
    model_id=model_id,
    messages=[
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
)
conversation_id = response.conversation_id
print(f"Conversation ID: {conversation_id}")
print(f"Request: {prompt}")
print(f"Response: {response.results[0].generated_text}")

print(heading("Continue with a conversation"))
prompt = "How can I start?"
response = client.text.chat.create(
    messages=[HumanMessage(content=prompt)],
    conversation_id=conversation_id,
    use_conversation_parameters=True,
)
print(f"Request: {prompt}")
print(f"Response: {response.results[0].generated_text}")
