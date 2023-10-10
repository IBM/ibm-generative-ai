import os
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv

from genai import Credentials

pytestmark = pytest.mark.integration

load_dotenv()

GENAI_API = os.getenv("GENAI_API")
GENAI_KEY = os.getenv("GENAI_KEY")


@pytest.fixture
def credentials(request):
    return Credentials(api_key=GENAI_KEY, api_endpoint=GENAI_API)


@pytest.fixture
def non_mocked_hosts(credentials) -> list:
    api_endpoint = urlparse(credentials.api_endpoint)
    return [api_endpoint.hostname]


def pytest_exception_interact(node, call, report):
    excinfo = call.excinfo
    if "script" in node.funcargs:
        excinfo.traceback = excinfo.traceback.cut(path=node.funcargs["script"])
    report.longrepr = node.repr_failure(excinfo)
