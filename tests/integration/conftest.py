import os

import pytest
from dotenv import load_dotenv

from genai import Credentials

pytestmark = pytest.mark.integration

load_dotenv()

WATSONX_API_ENDPOINT = os.getenv("WATSONX_API_ENDPOINT")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")


@pytest.fixture
def credentials(request):
    return Credentials(api_key=WATSONX_API_KEY, api_endpoint=WATSONX_API_ENDPOINT)
