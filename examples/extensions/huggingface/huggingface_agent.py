"""Run huggingface agent with genai models"""

from dotenv import load_dotenv

from genai import Client
from genai.credentials import Credentials
from genai.extensions.huggingface.agent import IBMGenAIAgent
from genai.text.generation import TextGenerationParameters


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


load_dotenv()

client = Client(credentials=Credentials.from_env())

print(heading("Use hugging face agent with genai sdk"))


agent = IBMGenAIAgent(
    client=client,
    model="meta-llama/llama-2-70b-chat",
    parameters=TextGenerationParameters(min_new_tokens=10, max_new_tokens=200),
)

agent.chat("Download the chat from the given url", url="https://research.ibm.com/blog/analog-ai-chip-low-power")
agent.chat("Summarize the downloaded chat")
