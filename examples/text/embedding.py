"""Get embedding vectors for text data"""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

inputs = ["Hello", "world"]
model_id = "sentence-transformers/all-minilm-l6-v2"

print(heading("Running embedding for inputs in parallel"))
# yields batch of results that are produced asynchronously and in parallel
for input, response in zip(inputs, client.text.embedding.create(model_id=model_id, inputs=inputs)):
    print(f"Embedding vector for '{input}': {response.results}")
