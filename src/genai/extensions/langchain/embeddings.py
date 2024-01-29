from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from genai._types import ModelLike
from genai.client import Client
from genai.schema import TextEmbeddingParameters
from genai.text.embedding.embedding_service import CreateExecutionOptions

__all__ = ["LangChainEmbeddingsInterface"]

try:
    from langchain_core.embeddings import Embeddings
    from langchain_core.runnables.config import run_in_executor
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")  # noqa: B904


class LangChainEmbeddingsInterface(BaseModel, Embeddings):
    """
    Class representing the LangChainChatInterface for interacting with the LangChain chat API.

    Example::

        from genai import Client, Credentials
        from genai.extensions.langchain import LangChainEmbeddingsInterface
        from genai.text.embedding import TextEmbeddingParameters

        client = Client(credentials=Credentials.from_env())
        embeddings = LangChainEmbeddingsInterface(
            client=client,
            model_id="sentence-transformers/all-minilm-l6-v2",
            parameters=TextEmbeddingParameters(truncate_input_tokens=True)
        )

        embeddings.embed_query("Hello world!")
        embeddings.embed_documents(["First document", "Second document"])
    """

    model_config = ConfigDict(extra="forbid", protected_namespaces=(), arbitrary_types_allowed=True)

    client: Client
    model_id: str
    parameters: Optional[ModelLike[TextEmbeddingParameters]] = None
    execution_options: Optional[ModelLike[CreateExecutionOptions]] = None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed search documents"""
        return self._get_embeddings(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed query text."""
        response = self._get_embeddings([text])
        return response[0]

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronous Embed query text."""
        return await run_in_executor(None, self.embed_query, text)

    async def aembed_documents(self, texts: List[str]) -> list[list[float]]:
        """Asynchronous Embed search documents"""
        return await run_in_executor(None, self.embed_documents, texts)

    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for response in self.client.text.embedding.create(
            model_id=self.model_id, inputs=texts, parameters=self.parameters, execution_options=self.execution_options
        ):
            embeddings.extend(response.results)

        return embeddings


LangChainEmbeddingsInterface.model_rebuild()
