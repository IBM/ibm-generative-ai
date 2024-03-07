import functools
from enum import Enum
from typing import Type

from pydantic import create_model

from genai._types import ApiBaseModel


@functools.cache
def _create_fallback_pydantic_model(cls_name: str):
    """Creates a pydantic model which allows access to arbitrary fields without throwing an error"""

    class RemovedApiModel(ApiBaseModel):
        def __getattr__(self, item):
            try:
                return super().__getattr__(item)
            except AttributeError:
                return None

    return create_model(cls_name, __base__=RemovedApiModel)


def _to_public_class_name(cls: Type) -> str:
    return cls.__name__.lstrip("_")


class _RemovedTuningType(str, Enum):
    PROMPT_TUNING = "prompt_tuning"
    MULTITASK_PROMPT_TUNING = "multitask_prompt_tuning"


_removed_schemas = {
    "TuningType": (
        "The 'TuningType' enum has been deprecated and will be removed in the future release, use string value instead."
        "To retrieve supported types, either see documentation or retrieve them via 'client.tune.types()' method.",
        _RemovedTuningType,
    ),
    "RequestChatConversationIdRetrieveResultsResponse": (
        "'RequestChatConversationIdRetrieveResultsResponse' has been replaced by 'dict[str, Any]'."
        "Do not use this class anymore.'",
        _create_fallback_pydantic_model("RequestChatConversationIdRetrieveResultsResponse"),
    ),
    "RequestChatConversationIdRetrieveResultsRequest": (
        "'RequestChatConversationIdRetrieveResultsRequest' has been replaced by 'dict[str, Any]'."
        "Do not use this class anymore.'",
        _create_fallback_pydantic_model("RequestChatConversationIdRetrieveResultsRequest"),
    ),
}
