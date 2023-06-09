import os

import pytest
from dotenv import load_dotenv

from genai import Credentials

pytestmark = pytest.mark.integration

load_dotenv()

WATSONX_API_ENDPOINT = os.getenv("GENAI_ENDPOINT")
WATSONX_API_KEY = os.getenv("GENAI_KEY")


@pytest.fixture
def credentials(request):
    return Credentials(api_key=WATSONX_API_KEY, api_endpoint=WATSONX_API_ENDPOINT)


def pytest_exception_interact(node, call, report):
    excinfo = call.excinfo
    if "script" in node.funcargs:
        excinfo.traceback = excinfo.traceback.cut(path=node.funcargs["script"])
    report.longrepr = node.repr_failure(excinfo)
