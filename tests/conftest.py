import re
from unittest.mock import patch

import pytest
from _pytest.fixtures import SubRequest
from pytest_httpx import HTTPXMock

from genai.services import AsyncResponseGenerator, ServiceInterface


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture
def non_mocked_hosts() -> list:
    return ["0.0.0.0"]


@pytest.fixture(autouse=True, scope="function")
def patch_generate_limits(request: SubRequest, httpx_mock: HTTPXMock):
    if "integration" in request.node.keywords:
        yield
    else:
        custom_params = request.param if hasattr(request, "param") else {}
        token_capacity = custom_params.get("tokens_capacity", 10)
        tokens_used = custom_params.get("tokens_used", 0)

        httpx_mock.add_response(
            url=re.compile(f".+{ServiceInterface.GENERATE_LIMITS}$"),
            method="GET",
            json={"tokenCapacity": token_capacity, "tokensUsed": tokens_used},
            status_code=200,
        )
        yield


@pytest.fixture(autouse=True, scope="function")
def patch_async_requests_limits(request: SubRequest):
    if "integration" in request.node.keywords:
        yield
        return

    custom_params = request.param if hasattr(request, "param") else {}
    sleep_duration = custom_params.get("duration", 0.1)
    with patch.multiple(AsyncResponseGenerator, LIMITS_CHECK_SLEEP_DURATION=sleep_duration):
        yield
