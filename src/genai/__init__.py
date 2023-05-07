import logging

from genai._version import __version__ as v
from genai.credentials import Credentials
from genai.metadata import Metadata
from genai.model import Model
from genai.prompt_pattern import PromptPattern

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["Model", "Credentials", "Metadata", "PromptPattern"]

__version__ = v
