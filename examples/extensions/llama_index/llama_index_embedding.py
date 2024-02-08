"""
Llamaindex Embeddings
"""
from dotenv import load_dotenv

from genai import Client, Credentials
from genai.extensions.llama_index import LlamaIndexEmbeddingsInterface
from genai.schema import TextEmbeddingParameters

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


print(heading("LlamaIndex Embeddings"))

client = Client(credentials=Credentials.from_env())
embeddings = LlamaIndexEmbeddingsInterface(
    client=client,
    model_id="sentence-transformers/all-minilm-l6-v2",
    parameters=TextEmbeddingParameters(truncate_input_tokens=True),
)

query_embedding = embeddings.get_query_embedding("Hello world!")
print(query_embedding)

documents_embedding = embeddings.get_agg_embedding_from_queries(["First document", "Second document"])
print(documents_embedding)
