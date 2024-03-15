from typing import Optional, Union

from pydantic import Field

from genai.schema import ModerationParameters, PromptTemplateData, TextGenerationParameters, TextTokenizationParameters
from genai.schema._api import _TextGenerationCreateRequest, _TextTokenizationCreateRequest


class TextGenerationCreateRequest(_TextGenerationCreateRequest):
    """Following properties are required for local server"""

    input: str
    model_id: str
    parameters: TextGenerationParameters = Field(default_factory=lambda: TextGenerationParameters())
    data: Optional[PromptTemplateData] = None
    input: Optional[str] = Field(None, examples=["How are you"], title="Input string")
    moderations: Optional[ModerationParameters] = None


class TextTokenizationCreateRequest(_TextTokenizationCreateRequest):
    """Following properties are required for local server"""

    model_id: str = Field(...)
    parameters: TextTokenizationParameters = Field(default_factory=lambda: TextTokenizationParameters())
    input: Optional[Union[str, list[str]]] = None
    prompt_id: Optional[str] = None


__all__ = ["TextGenerationCreateRequest", "TextTokenizationCreateRequest"]
