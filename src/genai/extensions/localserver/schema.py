from pydantic import Field

from genai._generated.api import (
    TextGenerationCreateRequest as _TextGenerationCreateRequest,
)
from genai._generated.api import (
    TextTokenizationCreateRequest as _TextTokenizationCreateRequest,
)
from genai.text.generation.schema import (
    TextGenerationParameters,
    TextGenerationReturnOptions,
)
from genai.text.tokenization.schema import TextTokenizationParameters

__all__ = [
    "TextGenerationParameters",
    "TextGenerationReturnOptions",
    "TextGenerationCreateRequest",
    "TextTokenizationCreateRequest",
]


class TextGenerationCreateRequest(_TextGenerationCreateRequest):
    """Following properties are required for local server"""

    input: str
    model_id: str
    parameters: TextGenerationParameters = Field(default_factory=lambda: TextGenerationParameters())


class TextTokenizationCreateRequest(_TextTokenizationCreateRequest):
    """Following properties are required for local server"""

    model_id: str
    parameters: TextTokenizationParameters = Field(default_factory=lambda: TextTokenizationParameters())
