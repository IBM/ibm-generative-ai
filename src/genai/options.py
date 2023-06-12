from typing import Any
from genai.utils.watsonx_helpers import watsonx_payload


class Options:
    def __init__(self, watsonx_template=None, watsonx_data=None, watsonx_files: list = None, *args, **kwargs) -> None:
        if watsonx_template:
            self.template = watsonx_payload(watsonx_template, watsonx_data, watsonx_files)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value

    def keys(self):
        return vars(self).keys()
