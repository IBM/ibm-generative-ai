import os
import re
from typing import Any, Optional
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
from _pytest.fixtures import SubRequest
from dotenv import load_dotenv
from pytest_httpx import HTTPXMock
from vcr.cassette import Cassette
from vcr.request import Request

from genai import Client, Credentials
from genai._generated.endpoints import ApiEndpoint, TextGenerationLimitRetrieveEndpoint
from genai._utils.async_executor import BaseConfig
from genai._utils.service import BaseService
from genai.text.generation.limits import (
    ConcurrencyLimit,
    TextGenerationLimit,
    TextGenerationLimitRetrieveResponse,
)
from tests.helpers import (
    match_endpoint,
    parse_vcr_response_body,
    path_ignore_id_matcher,
)


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture(scope="function")
def credentials():
    load_dotenv()
    api_key = os.getenv("GENAI_KEY")
    endpoint = os.getenv("GENAI_API")
    return Credentials(api_key, endpoint)


@pytest.fixture(scope="function")
def client(request, credentials: Credentials) -> Client:
    return Client(credentials=credentials)


@pytest.fixture
def non_mocked_hosts() -> list:
    return ["0.0.0.0"]


def pytest_recording_configure(config, vcr):
    vcr.register_matcher("path_ignore_id", path_ignore_id_matcher)


def _compose_vcr_transformers(transformers):
    def _combined_transformer(request_or_response):
        for transformer in transformers:
            request_or_response = transformer(request_or_response)
        return request_or_response

    return _combined_transformer


@pytest.fixture(scope="module")
def vcr_config():
    def _anonymize_host(request):
        hostname = urlparse(request.uri).hostname
        request.uri = request.uri.replace(hostname, "api.com")
        return request

    def _normalize_multipart_boundary_hash(request):
        """
        The Content-Type: multipart/form-data; boundary=*boundary-hash*, contains some random hash for boundary in httpx
        We replace it with the keyword BOUNDARY both in the header an in the request body
        """
        header_pattern = re.compile(r"multipart/form-data; boundary=([a-zA-Z0-9]*)")
        for key, header in request.headers.items():
            if match := header_pattern.match(header):
                [boundary] = match.groups()
                request.body = request.body.decode("utf-8").replace(boundary, "BOUNDARY").encode("utf-8")
                request.headers[key] = request.headers[key].replace(boundary, "BOUNDARY")
                break
        return request

    def _filter_response_headers(response):
        response["headers"].pop("Set-Cookie", None)
        return response

    return {
        "filter_headers": ["authorization", "user-agent", "x-request-origin", "cookie", "host"],
        "match_on": ["method", "path", "query", "body"],
        "before_record_request": _compose_vcr_transformers([_anonymize_host, _normalize_multipart_boundary_hash]),
        "before_record_response": _compose_vcr_transformers([_filter_response_headers]),
        "decode_compressed_response": True,
        "ignore_hosts": [
            "huggingface.co",  # requests cannot be captured because they are influenced by the operating system
        ],
    }


@pytest.fixture(scope="function")
def patch_generate_limits(request: SubRequest, httpx_mock: HTTPXMock):
    custom_params = request.param if hasattr(request, "param") else {}
    token_capacity = custom_params.get("tokens_capacity", 10)
    tokens_used = custom_params.get("tokens_used", 0)

    httpx_mock.add_response(
        url=match_endpoint(TextGenerationLimitRetrieveEndpoint),
        method="GET",
        json=TextGenerationLimitRetrieveResponse(
            result=TextGenerationLimit(
                concurrency=ConcurrencyLimit(limit=token_capacity, remaining=token_capacity - tokens_used)
            )
        ).model_dump(),
    )
    yield


@pytest.fixture(scope="function")
def get_vcr_responses_of(credentials: Credentials, vcr: Optional[Cassette]):
    if vcr is None:
        raise RuntimeError("Test must be marked as 'vcr' in order to use the `get_vcr_responses_of` fixture")

    def _get_vcr_response_of(
        api_endpoint: type[ApiEndpoint],
        body: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
        **params,
    ) -> list[dict[str, Any]]:
        """
        Search for requests matching the criteria specified by params
        Returns: flattened responses to all found requests,
            narrow down your search (e.g., include body) if you want to reduce the number of matched requests to 1
        """
        endpoint = credentials.api_endpoint + BaseService._get_endpoint(api_endpoint, **params)
        request = Request(method=api_endpoint.method, uri=endpoint, body=body or {}, headers=headers or {})
        response_data = []
        for found_request, _, _ in vcr.find_requests_with_most_matches(request):
            for response in vcr.responses_of(found_request):
                response_data.extend(parse_vcr_response_body(response))
        return response_data

    return _get_vcr_response_of


@pytest.fixture(scope="function")
def patch_async_requests_limits(request: SubRequest):
    if "integration" in request.node.keywords:
        yield
        return

    custom_params = request.param if hasattr(request, "param") else {}
    sleep_duration = custom_params.get("duration", 0.1)
    with patch.multiple(BaseConfig, limit_reach_retry_threshold=sleep_duration):
        yield
