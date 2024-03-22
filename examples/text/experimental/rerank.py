"""
Document reranking

Rerank documents based on their relevancy to the input query.
"""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import TextRerankParameters, TextRerankReturnOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

print(heading("EXPERIMENTAL: Text Reranking"))
response = client.text.experimental.rerank.create(
    model_id="sentence-transformers/all-minilm-l6-v2",
    query="What is Python?",
    documents=[
        "Python supports multiple programming paradigms.",
        "Python is heavily used by data scientist.",
        "Python is a high-level, interpreted programming language known for its clear syntax and code readability.",
        "Python enables developers to write clear, logical code for small and large-scale projects.",
    ],
    parameters=TextRerankParameters(
        truncate_input_tokens=True, return_options=TextRerankReturnOptions(documents=True, query=True, top_n=3)
    ),
)

print(f"Query: {response.result.query}")
print("")

for rank, result in enumerate(response.result.results, start=1):
    print(f"Ranking {rank}/{len(response.result.results)}")
    print(f"-> Score: {result.score}")
    print(f"-> Document: {result.document}")
    print(f"-> Input Index: {result.index}")
    print("")
