import asyncio
from typing import Optional

from genai._types import ModelLike
from genai.client import Client
from genai.schema import TextEmbeddingParameters
from genai.text.embedding.embedding_service import CreateExecutionOptions

try:
    from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding
except ImportError:
    raise ImportError("Could not import llamaindex: Please install ibm-generative-ai[llama-index] extension.")  # noqa: B904


class IBMGenAILlamaIndexEmbedding(BaseEmbedding):
    client: Client
    model_id: str
    parameters: Optional[ModelLike[TextEmbeddingParameters]] = None
    execution_options: Optional[ModelLike[CreateExecutionOptions]] = None

    @classmethod
    def class_name(cls) -> str:
        return "IBMGenAIEmbedding"

    def _get_query_embedding(self, query: str) -> Embedding:
        response = self._get_embeddings([query])
        return response[0]

    def _get_text_embedding(self, text: str) -> Embedding:
        response = self._get_embeddings([text])
        return response[0]

    def _get_text_embeddings(self, texts: list[str]) -> list[Embedding]:
        response = self._get_embeddings(texts)
        return response

    async def _aget_query_embedding(self, query: str) -> Embedding:
        return await asyncio.get_running_loop().run_in_executor(None, self._get_query_embedding, query)

    async def _aget_text_embedding(self, text: str) -> Embedding:
        return await asyncio.get_running_loop().run_in_executor(None, self._get_text_embedding, text)

    async def _aget_text_embeddings(self, texts: list[str]) -> list[Embedding]:
        return await asyncio.get_running_loop().run_in_executor(None, self._get_text_embeddings, texts)

    def _get_embeddings(self, texts: list[str]) -> list[Embedding]:
        embeddings: list[list[float]] = []
        for response in self.client.text.embedding.create(
            model_id=self.model_id, inputs=texts, parameters=self.parameters, execution_options=self.execution_options
        ):
            embeddings.extend(response.results)

        return embeddings
