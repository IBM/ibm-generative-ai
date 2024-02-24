from enum import Enum
from typing import Type


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
    )
}
