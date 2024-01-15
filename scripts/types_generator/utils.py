import re
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from types_generator.logger import get_logger

logger = get_logger(__name__)


def from_camel_case_to_snake_case(input: str) -> str:
    return re.sub("([A-Z]+)", r"_\1", input).lower()


def serialize_model_definition(model: type[BaseModel]) -> str:
    template = f"class {model.__name__}:\n"
    template += "\t__slots__ = ()\n"

    for k, v in model.model_fields.items():
        assert v.annotation
        template += f"\t{k}: {v.annotation.__name__}\n"

    return template


def serialize_model(name: str, model: dict, base_model: str) -> str:
    if not model:
        return ""

    template = f"class {name}({base_model}):\n"

    conversion_map: dict[str, Callable[[Any], str]] = {
        "str": lambda value: f"'{value}'",
        "int": lambda value: f"{value}",
        "float": lambda value: f"{float}",
        "bool": lambda value: f"{str(value)}",
    }

    for k, v in model.items():
        date_type = type(v).__name__
        handler = conversion_map.get(date_type)
        assert handler
        template += f"\t{k}: {date_type} = {handler(v)}\n"

    return template


def dump_model(serialized: str, target: Path) -> None:
    if not serialized:
        raise Exception("Provided model is empty. Nothing to dump.")

    logger.info(f"Saving to {target.resolve()}")
    logger.debug(serialized)
    target.write_text(serialized)
