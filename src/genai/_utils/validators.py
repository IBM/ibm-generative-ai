from __future__ import annotations

from typing import Any, Optional, TypeVar


def assert_is_not_empty_string(input: Any):
    if not isinstance(input, str):
        raise TypeError(f"Provided value '{input}' is not a string!")
    if input == "":
        raise ValueError("Provided value must be non empty!")


T = TypeVar("T")


def assert_is_instanceof(input: Optional[T], target: type[T]):
    assert isinstance(input, target)
    if not input or not isinstance(input, target):
        raise ValueError(f"Provided value '{input}' is not instance of {target.__name__}!")
