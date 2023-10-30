import pytest
from pytest_httpx import HTTPXMock

from genai.schemas import HistoryParams
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate


@pytest.mark.unit
class TestHistory:
    def setup_method(self):
        # mock object for the API call
        self.service = ServiceInterface(service_url="http://service_url", api_key="API_KEY")
        # test all GenerateParams fields

    @pytest.fixture
    def params(self):
        return HistoryParams(
            limit=10,
            offset=0,
            status="SUCCESS",
            origin="API",
        )

    def test_history_api_call(self, params, httpx_mock: HTTPXMock):
        response = SimpleResponse.history()
        httpx_mock.add_response(
            url=match_endpoint(ServiceInterface.HISTORY, query_params=params), method="GET", json=response
        )

        g = self.service.history(params=params)
        assert g.json() == response

    def test_history_general_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(
            Exception("some general error"), url=match_endpoint(ServiceInterface.HISTORY), method="GET"
        )
        with pytest.raises(BaseException, match="some general error"):
            self.service.history()
