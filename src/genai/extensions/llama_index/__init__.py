"""Extension for LLamaIndex library"""

from genai.extensions.llama_index.embeddings import IBMGenAILlamaIndexEmbedding
from genai.extensions.llama_index.llm import IBMGenAILlamaIndex

__all__ = ["IBMGenAILlamaIndex", "IBMGenAILlamaIndexEmbedding"]
