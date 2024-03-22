from enum import Enum
from typing import Optional, Type

from pydantic import Field

from genai._types import ApiBaseModel
from genai.schema._api import PromptTemplateData


def _to_public_class_name(cls: Type) -> str:
    return cls.__name__.lstrip("_")


class _RemovedTuningType(str, Enum):
    PROMPT_TUNING = "prompt_tuning"
    MULTITASK_PROMPT_TUNING = "multitask_prompt_tuning"


class _ImplicitHateOptions(ApiBaseModel):
    send_tokens: Optional[bool] = False
    threshold: Optional[float] = Field(0.75, gt=0.0, lt=1.0)


class _StigmaOptions(ApiBaseModel):
    send_tokens: Optional[bool] = False
    threshold: Optional[float] = Field(0.75, gt=0.0, lt=1.0)


class _PromptTemplate(ApiBaseModel):
    data: PromptTemplateData
    id: Optional[str] = None
    value: Optional[str] = None


_removed_schemas = {
    "TuningType": (
        "The 'TuningType' enum has been deprecated and will be removed in the future release, use string value instead."
        "To retrieve supported types, either see documentation or retrieve them via 'client.tune.types()' method.",
        _RemovedTuningType,
    ),
    "ImplicitHateOptions": (
        "The 'ImplicitHateOptions' class and appropriate ImplicitHate model has been deprecated, "
        "use 'SocialBiasOptions' instead.",
        _ImplicitHateOptions,
    ),
    "StigmaOptions": (
        "The 'StigmaOptions' class and appropriate Stigma model has been deprecated, use SocialBiasOptions instead.",
        _StigmaOptions,
    ),
    "PromptTemplate": ("The 'PromptTemplate' has been deprecated and is not used anymore.", _PromptTemplate),
}
