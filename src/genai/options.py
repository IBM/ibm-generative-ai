from typing import Any

from genai.utils.watsonx_helpers import watsonx_payload


class Options:
    def __init__(
        self,
        watsonx_template=None,
        watsonx_data=None,
        watsonx_files: list = None,
        *args,
        **kwargs,
    ) -> None:
        self.d = {}
        if watsonx_template:
            self.d["template"] = watsonx_payload(watsonx_template, watsonx_data, watsonx_files)
        self.d.update(kwargs)

    def __getitem__(self, key) -> Any:
        return self.d[key]

    def keys(self):
        return self.d.keys()
