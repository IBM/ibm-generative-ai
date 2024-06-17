from typing import Type


def _to_public_class_name(cls: Type) -> str:
    return cls.__name__.lstrip("_")


_removed_schemas = {}
