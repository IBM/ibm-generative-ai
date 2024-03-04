import logging

import pytest
from httpx import Request
from httpx._auth import FunctionAuth
from pytest_httpx import HTTPXMock

from genai import Client, Credentials
from genai.schema import TextGenerationLimitRetrieveEndpoint
from tests.helpers import match_endpoint

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestApiClient:
    def test_default_auth_header(self, patch_generate_limits, httpx_mock: HTTPXMock):
        test_api_key = "test_api_key"
        client = Client(credentials=Credentials(api_key=test_api_key))

        client.text.generation.limit.retrieve()
        request = httpx_mock.get_request(url=match_endpoint(TextGenerationLimitRetrieveEndpoint))

        assert request.headers.get("Authorization") == f"Bearer {test_api_key}"

    def test_custom_auth_header(self, patch_generate_limits, httpx_mock: HTTPXMock):
        custom_auth_header = "CUSTOM_AUTH_HEADER"
        custom_auth_fn_called = False

        def _custom_auth_fn(request: Request) -> Request:
            nonlocal custom_auth_fn_called
            custom_auth_fn_called = True
            request.headers["Authorization"] = custom_auth_header
            return request

        client = Client(
            credentials=Credentials(api_key="dummy_api_key"),
            config={"api_client_config": {"client_options": {"auth": FunctionAuth(_custom_auth_fn)}}},
        )

        client.text.generation.limit.retrieve()
        request = httpx_mock.get_request(url=match_endpoint(TextGenerationLimitRetrieveEndpoint))

        assert custom_auth_fn_called
        assert request.headers.get("Authorization") == custom_auth_header
