from pydantic import Field

from genai.schema import TextGenerationParameters, TextTokenizationParameters
from genai.schema._api import _TextGenerationCreateRequest, _TextTokenizationCreateRequest


class TextGenerationCreateRequest(_TextGenerationCreateRequest):
    """Following properties are required for local server"""

    input: str
    model_id: str
    parameters: TextGenerationParameters = Field(default_factory=lambda: TextGenerationParameters())


class TextTokenizationCreateRequest(_TextTokenizationCreateRequest):
    """Following properties are required for local server"""

    model_id: str
    parameters: TextTokenizationParameters = Field(default_factory=lambda: TextTokenizationParameters())


__all__ = ["TextGenerationCreateRequest", "TextTokenizationCreateRequest"]
