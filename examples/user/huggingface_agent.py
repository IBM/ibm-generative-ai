import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.extensions.huggingface.agent import IBMGenAIAgent
from genai.schemas import GenerateParams

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

creds = Credentials(api_key, api_endpoint)
params = GenerateParams(min_new_tokens=10, max_new_tokens=200)

agent = IBMGenAIAgent(credentials=creds, model="meta-llama/llama-2-70b-chat", params=params)

agent.chat("Download the text from the given url", url="https://research.ibm.com/blog/analog-ai-chip-low-power")
agent.chat("Summarize the downloaded text")
