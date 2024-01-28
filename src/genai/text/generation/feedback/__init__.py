"""Modules containing functionalities related to text generation feedback"""

from genai.text.generation.feedback.feedback_service import *


def __getattr__(name: str):
    """Allow additional imports for backward compatibility with old import system "from genai.service_name import"."""
    if name in globals():
        return globals()[name]

    from genai._utils.deprecated_schema_import import _deprecated_schema_import

    return _deprecated_schema_import(name, __name__)
