from typing import Any


class Options:
    def __init__(self, watsonx_template=None, watsonx_data=None, watsonx_files: list = None, *args, **kwargs) -> None:
        if watsonx_template:
            self.template = self.watsonx_payload(watsonx_template, watsonx_data, watsonx_files)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value

    def keys(self):
        return vars(self).keys()

    def watsonx_payload(self, template, data=None, files=None):
        _dict = {}
        _dict["data"] = {}

        try:
            _dict["id"] = template.watsonx.id

            if data:
                _dict["data"] = data

            if files:
                _dict["data"]["example_file_ids"] = files

            return _dict

        except Exception as e:
            print(e)
