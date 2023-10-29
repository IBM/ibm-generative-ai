import pytest
from pytest_httpx import HTTPXMock

from genai import Credentials, Metadata
from genai.schemas.responses import HistoryResponse, TermsOfUse
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint


@pytest.mark.unit
class TestMetadata:
    def test_accept_TOU(self, httpx_mock: HTTPXMock):
        """Tests that we can accept the TOU"""

        TOU_RESPONSE = SimpleResponse.terms_of_use()
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.TOU), method="PATCH", json=TOU_RESPONSE)

        # Build up our Model Object
        creds = Credentials("TEST_API_KEY")

        # Instantiate the GENAI Proxy Object
        model_meta = Metadata(creds)

        tou_response = model_meta.accept_terms_of_use()
        original_tou = TermsOfUse(**TOU_RESPONSE)
        assert tou_response == original_tou

    def test_history(self, httpx_mock: HTTPXMock):
        """Tests that we can get the History"""

        HISTORY_RESPONSE = SimpleResponse.history()
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.HISTORY), method="GET", json=HISTORY_RESPONSE)

        # Build up our Model Object
        creds = Credentials("TEST_API_KEY")

        # Instantiate the GENAI Proxy Object
        model_meta = Metadata(creds)

        history_response = model_meta.get_history()
        original_history_response = HistoryResponse(**HISTORY_RESPONSE)
        assert history_response == original_history_response
