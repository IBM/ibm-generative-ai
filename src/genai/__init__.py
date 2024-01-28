import logging

from genai._utils.api_client import ApiClient
from genai._utils.shared_loop import handle_shutdown_event
from genai._version import __version__ as v
from genai.client import Client
from genai.credentials import Credentials

__version__ = v


__all__ = ["Client", "ApiClient", "Credentials", "handle_shutdown_event", "__version__"]
