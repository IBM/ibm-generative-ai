from re import Pattern, compile
from typing import Union
from urllib.parse import urlencode

from pydantic import BaseModel

from genai.utils.request_utils import sanitize_params


def match_endpoint(*paths: str, query_params: Union[dict, BaseModel, str] = "") -> Pattern:
    endpoint = "/".join(paths)
    if isinstance(query_params, BaseModel):
        query_params = sanitize_params(query_params)
    if isinstance(query_params, dict):
        query_params = "\\?" + urlencode(query_params)

    return compile(f".+{endpoint}{query_params}$")
