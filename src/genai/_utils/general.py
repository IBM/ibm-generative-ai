import functools
import hashlib
import json
from enum import Enum
from typing import Any, Callable, Generator, Mapping, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from genai._types import EnumLike

TModel = TypeVar("TModel", bound=BaseModel)


def to_model_optional(
    input_params: Union[Any, list[Any]], Model: Type[TModel], *, copy: bool = True
) -> Optional[TModel]:
    return to_model_instance(input_params, Model, copy=copy) if input_params else None


def to_model_instance(input_params: Union[Any, list[Any]], Model: Type[TModel], *, copy: bool = True) -> TModel:
    """
    Converts input parameters to an instance of the specified Pydantic model.

    Args:
        input_params (Union[Any, list[Any]]): The input parameters to convert.
        Model (Type[TModel]): The type of model to convert to.
        copy (bool, optional): Determines whether to create a copy of the model instance. Defaults to True.

    Returns:
        TModel: An instance of the specified model.

    Raises:
        ValueError: If the 'params' property is not an instance of the specified Model class.

    """
    if not input_params:
        return Model()

    if isinstance(input_params, list):
        result = merge_objects(
            *[
                (
                    obj
                    if isinstance(obj, dict)
                    else to_model_instance(obj, Model).model_dump(exclude_none=True, exclude_defaults=True)
                )
                for obj in input_params
                if obj
            ]
        )
        return Model(**result)

    params = input_params
    if isinstance(params, Model):
        if not copy:
            return params

        return params.model_copy()

    if isinstance(params, BaseModel):
        return Model(**params.model_dump())

    if isinstance(params, dict):
        return Model(**params)

    raise ValueError(f"The 'params' property should be an instance of {Model.__name__} class. Current value: {params}")


def to_model_instance_if_defined(
    input_params: Union[Any, list[Any]], Model: Type[TModel], *, copy: bool = True
) -> Union[TModel, None]:
    return to_model_instance(input_params, Model, copy=copy) if input_params is not None else None


TInput = TypeVar("TInput")


def batch(inputs: list[TInput], *, chunk_size: int) -> list[list[TInput]]:
    if chunk_size <= 0:
        raise ValueError("'chunk_size' must be > 0")

    return [inputs[i : i + chunk_size] for i in range(0, len(inputs), chunk_size)]


def batch_by_size_constraint(
    inputs: list[str], *, max_chunk_size: Optional[int] = None, max_size_bytes: Optional[int] = None
) -> Generator[list[str], None, None]:
    """
    Args:
        inputs: A list of strings representing the inputs to be batched.
        max_chunk_size: An optional integer representing the maximum number of inputs in each batch.
        max_size_bytes: An optional integer representing the maximum total size in bytes for each batch.

    Returns:
        A generator that yields batches of inputs, where each batch is a list of strings.

    Raises:
        ValueError: If both max_chunk_size and max_size_bytes are None.
        ValueError: If max_chunk_size is less than 1.
        ValueError: If max_size_bytes is less than 1.
        ValueError: If a single input is larger than the maximal payload size.

    """
    if max_size_bytes is None and max_chunk_size is None:
        yield inputs.copy()
        return

    if max_size_bytes is None:
        yield from batch(inputs, chunk_size=max_chunk_size or len(inputs))
        return

    if max_chunk_size is None:
        max_chunk_size = len(inputs)

    if max_chunk_size < 1:
        raise ValueError("'chunk_size' must be >= 1")

    if max_size_bytes is None or max_size_bytes < 1:
        raise ValueError("'max_size_bytes' must be >= 1")

    chunk: list[str] = []
    chunk_size = 0

    for input in inputs:
        size = len(input.encode("utf-8"))
        if chunk_size + size > max_size_bytes or len(chunk) == max_chunk_size:
            if not chunk:
                raise ValueError(
                    f"Single input is larger than maximal payload size. Input size: {size}B. Allowed size: {max_size_bytes}B"  # noqa
                )

            yield chunk
            chunk = []
            chunk_size = 0

        chunk.append(input)
        chunk_size += size

    if chunk:
        yield chunk


_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


def merge_objects(*objs: Optional[Mapping[_KT, _VT]]) -> dict[_KT, _VT]:
    result: dict[_KT, _VT] = {}
    for obj in objs:
        if obj is not None:
            result.update(obj)
    return result


def cast_list(input: Union[TInput, list[TInput]]) -> list[TInput]:
    return input if isinstance(input, list) else [input]


def first_defined(*args: Optional[TInput], default: TInput) -> TInput:
    return next((v for v in args if v is not None), default)


E = TypeVar("E", bound=Enum)


def to_enum(cls: type[E], value: EnumLike[E]) -> E:
    return cls(value)


def to_enum_optional(value: Optional[EnumLike[E]], cls: type[E]) -> Optional[E]:
    return None if value is None else cls(value)


def hash_params(**kwargs):
    dhash = hashlib.md5()
    dhash.update(json.dumps(kwargs, sort_keys=True, default=str).encode())
    return dhash.hexdigest()


T = TypeVar("T", bound=Callable)


def single_execution(fn: T) -> T:
    return functools.cache(fn)  # type: ignore


def prompts_to_strings(prompts: Union[list[str], str, None]) -> list[str]:
    if prompts is None:
        return []

    if not isinstance(prompts, list):
        return [prompts]

    return prompts
