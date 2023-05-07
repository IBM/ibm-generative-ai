# A stripped down and modified version of some definitions in
# https://github.com/pandas-dev/pandas/blob/2.0.x/pandas/core/accessor.py
import logging

logger = logging.getLogger(__name__)


class AccessorRegistry:
    def __init__(self, key: str, accessor) -> None:
        self.key = key
        self.accessor = accessor

    def __get__(self, obj, cls):
        if obj is None:
            return self.accessor
        accessor_obj = self.accessor(obj)
        object.__setattr__(obj, self.key, accessor_obj)
        return accessor_obj


def _register_accessor(key, cls):
    def wrapper(accessor):
        setattr(cls, key, AccessorRegistry(key, accessor))
        cls._accessors.add(key)
        return wrapper

    return wrapper


def register_promptpattern_accessor(name: str):
    from genai import PromptPattern

    # The line below defines a parameterized decorator
    # The effect of lines below is to call the wrapper inside the
    # paramterized decorator with accessor as "A".
    # @register_accessor("extension_name", PromptPattern)
    # class A():
    return _register_accessor(name, PromptPattern)
