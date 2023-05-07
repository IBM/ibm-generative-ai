from unittest.mock import MagicMock, patch

import pytest

from genai.schemas import HistoryParams
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate


@pytest.mark.unit
class TestHistory:
    def setup_method(self):
        # mock object for the API call
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        # test all GenerateParams fields

    @pytest.fixture
    def params(self):
        return HistoryParams(
            limit=10,
            offset=0,
            status="SUCCESS",
            origin="API",
        )

    @patch("genai.services.RequestHandler.get")
    def test_history_api_call(self, mock_requests, params):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.history()
        mock_requests.return_value = mock_response

        g = self.service.history(params=params)
        assert g == mock_response

    @patch("genai.services.RequestHandler.get", side_effect=Exception("some general error"))
    def test_history_general_exception(self, mock):
        with pytest.raises(BaseException, match="some general error"):
            self.service.history()
