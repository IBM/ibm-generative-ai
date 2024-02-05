"""
Run Transformers Agents

.. admonition:: Python 3.12 support
    :class: warning

    The huggingface extension (:bash:`pip install 'ibm-generative-ai[huggingface]'`) is not supported in python 3.12 yet
    due to the lack of pytorch support for 3.12.
    Follow the `pytorch issue <https://github.com/pytorch/pytorch/issues/110436>`_ for more information.
"""

from dotenv import load_dotenv

from genai import Client
from genai.credentials import Credentials
from genai.extensions.huggingface.agent import IBMGenAIAgent
from genai.schema import TextGenerationParameters


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


load_dotenv()

client = Client(credentials=Credentials.from_env())

print(heading("Transformers Agent"))


agent = IBMGenAIAgent(
    client=client,
    model="meta-llama/llama-2-70b-chat",
    parameters=TextGenerationParameters(min_new_tokens=10, max_new_tokens=200, random_seed=777, temperature=0),
)

agent.chat("Extract text from the given url", url="https://research.ibm.com/blog/analog-ai-chip-low-power")
agent.chat("Do the text summarization on the downloaded text.")
