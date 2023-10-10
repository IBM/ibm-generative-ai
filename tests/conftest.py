import re

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_httpx import HTTPXMock

from genai.services import ServiceInterface


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture
def non_mocked_hosts() -> list:
    return ["0.0.0.0"]


@pytest.fixture(autouse=True, scope="function")
def patch_generate_limits(request: FixtureRequest, httpx_mock: HTTPXMock):
    if "integration" in request.node.keywords:
        return

    httpx_mock.add_response(
        url=re.compile(f".+{ServiceInterface.GENERATE_LIMITS}"),
        json={"tokenCapacity": 10, "tokensUsed": 0},
        method="GET",
        status_code=200,
    )
