"""Extension for LLamaIndex library"""

from genai.extensions.llama_index.embeddings import LlamaIndexEmbeddingsInterface
from genai.extensions.llama_index.llm import IBMGenAILlamaIndex

__all__ = ["IBMGenAILlamaIndex", "LlamaIndexEmbeddingsInterface"]
