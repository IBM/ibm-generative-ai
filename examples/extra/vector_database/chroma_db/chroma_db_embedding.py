"""
Create ChromaDB Embedding Function
"""

from typing import Optional

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv

from genai import Client, Credentials
from genai.schema import TextEmbeddingParameters

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


class ChromaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, *, model_id: str, client: Client, parameters: Optional[TextEmbeddingParameters] = None):
        self._model_id = model_id
        self._parameters = parameters
        self._client = client

    def __call__(self, inputs: Documents) -> Embeddings:
        embeddings: Embeddings = []
        for response in self._client.text.embedding.create(
            model_id=self._model_id, inputs=inputs, parameters=self._parameters
        ):
            embeddings.extend(response.results)

        return embeddings


credentials = Credentials.from_env()
client = Client(credentials=credentials)
embedding_fn = ChromaEmbeddingFunction(model_id="sentence-transformers/all-minilm-l6-v2", client=client)

print(embedding_fn(["Hello world!"]))
