"""Extension for running local simplified inference API compatible with current version of SDK"""

from genai.extensions.localserver.local_api_server import LocalLLMServer
from genai.extensions.localserver.local_base_model import LocalModel

__all__ = ["LocalModel", "LocalLLMServer"]
