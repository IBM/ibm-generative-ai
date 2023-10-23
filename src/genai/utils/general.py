from typing import Any, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def to_model_instance(params: Any, Model: Type[T]) -> T:
    if params is None:
        return Model()

    if isinstance(params, Model):
        return params.model_copy()

    if isinstance(params, dict):
        return Model(**params)

    raise ValueError(f"The 'params' property should be an instance of {Model.__name__} class. Current value: {params}")
