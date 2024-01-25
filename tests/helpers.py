import functools
import inspect
import json
import re
from dataclasses import dataclass
from re import compile
from typing import Any, Iterator, Protocol, TypeVar, Union
from urllib.parse import parse_qs, quote

from httpx import Response
from httpx_sse import EventSource
from pydantic import BaseModel

import genai
from genai._generated.endpoints import ApiEndpoint

_PATH_TEMPLATE_PARAMS = re.compile(r"{([a-zA-Z_][a-zA-Z0-9_]*)}")
_ID_REGEX = re.compile(".*[iI]d")


class _ModelWithEndpoint(Protocol):
    path: str = ""


T = TypeVar("T", bound=_ModelWithEndpoint)


def match_endpoint(
    *matchers: Union[str, type[T]],
    query_params: Union[dict, BaseModel, str] = "",
    property_name: str = "path",
    append_version=True,
):
    paths = [model if isinstance(model, str) else getattr(model(), property_name) for model in matchers]
    endpoint = "/".join(paths)

    query_params = {
        **(
            query_params.model_dump(exclude_none=True)
            if isinstance(query_params, BaseModel)
            else query_params.copy()
            if isinstance(query_params, dict)
            else parse_qs(query_params)
        )
    }

    def _create_query_parameter_matcher(key: str, value: str, *, escape: bool):
        return f"(?=.*{key}={quote(str(value)) if escape else value})"

    query_params_matchers = [
        _create_query_parameter_matcher(key, value, escape=False) for key, value in query_params.items()
    ]
    if "version" not in query_params and append_version:
        version_param = _create_query_parameter_matcher("version", r"\d{4}-\d{2}-\d{2}", escape=False)
        query_params_matchers.append(version_param)

    return compile(f".+{endpoint}{''.join(query_params_matchers) if query_params_matchers else ''}")


def compare_responses(response: BaseModel, expected: Union[dict, BaseModel]):
    if isinstance(expected, BaseModel):
        assert response == expected
    else:
        assert response.model_dump(mode="json") == expected


@dataclass(frozen=True)
class EndpointTemplate:
    path: str
    params: tuple[str, ...]
    id_params: tuple[str, ...]
    regex_for_url_match: re.Pattern


@functools.cache
def _get_endpoints_with_ids():
    endpoints_with_ids: set[EndpointTemplate] = set()
    for _, member_class in inspect.getmembers(genai._generated.endpoints):
        if not inspect.isclass(member_class):
            continue
        if issubclass(member_class, ApiEndpoint) and member_class != ApiEndpoint:
            path = member_class.path
            if not (params := _PATH_TEMPLATE_PARAMS.findall(path)):
                continue
            if not (id_params := {param for param in params if _ID_REGEX.match(param)}):
                continue

            path_with_groups = path
            for param in params:
                if param in id_params:
                    path_with_groups = path_with_groups.replace(f"{{{param}}}", "[^/]*")  # do not capture ids
                else:
                    path_with_groups = path_with_groups.replace(f"{{{param}}}", "([^/]*)")  # capture other params
            regex_for_url_match = re.compile(rf"^{path_with_groups}$")
            endpoints_with_ids.add(EndpointTemplate(path, tuple(params), tuple(id_params), regex_for_url_match))

    return endpoints_with_ids


def path_ignore_id_matcher(r1, r2):
    """
    Match requests path, but ignore any ids based on template, for example:
        template = /v2/tunes/{id}/content/{type}
        r1: /v2/tunes/123/content/vectors
        r2: /v2/tunes/456/content/vectors
        MATCH

        r1: /v2/tunes/123/content/vectors
        r2: /v2/tunes/456/content/export
        NO MATCH

    TODO: I thought I'd need this elaborate matcher, but turns out it's not necessary.
    Might be useful sometime later though when we want to ignore IDs in request url.
    """
    match = False
    if r1.path == r2.path:
        match = True
    for endpoint_template in _get_endpoints_with_ids():
        match1 = endpoint_template.regex_for_url_match.match(r1.path)
        match2 = endpoint_template.regex_for_url_match.match(r2.path)
        if match1 and match2 and match1.groups() == match2.groups():
            return True
    return match


def parse_vcr_response_body(response: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Extract data from application/json or text/event-stream response casette"""
    headers = response["headers"]
    content_type = headers.get("Content-Type", headers.get("content-type"))[0]
    if content_type.startswith("application/json"):
        yield json.loads(response["body"]["string"])
    elif content_type.startswith("text/event-stream"):
        httpx_response = Response(
            content=response["body"]["string"],
            headers={header: value[0] for header, value in response["headers"].items()},
            status_code=response["status"]["code"],
        )
        for event in EventSource(httpx_response).iter_sse():
            if event.data:
                yield json.loads(event.data)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")
