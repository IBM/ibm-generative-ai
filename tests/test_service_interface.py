from unittest.mock import MagicMock, patch

import pytest

from genai.schemas import GenerateParams, ReturnOptions
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestServiceInterface:
    def setup_method(self):
        # mock object for the API call
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def params(seld):
        return GenerateParams(decoding_method="greedy", return_options=ReturnOptions(input_text=True))

    @patch("genai.services.RequestHandler.patch")
    def test_tou(self, mocked_post_request):
        expected_resp = SimpleResponse.terms_of_use()
        expected = MagicMock(status_code=200, json=expected_resp)
        mocked_post_request.return_value = expected

        resp = self.service.terms_of_use(True)

        assert resp == expected
        assert resp.status_code == 200

    @patch("genai.services.RequestHandler.patch", side_effect=Exception("some general error"))
    def test_tou_exception(self, mock):
        with pytest.raises(BaseException, match="some general error"):
            self.service.terms_of_use(True)

    def test_sanitize_params(self, params):
        new_dict = ServiceInterface._sanitize_params(params=params)

        assert isinstance(new_dict, dict)
        assert "min_new_tokens" not in new_dict
