import pytest
from pytest_httpx import HTTPXMock

from genai.schemas import GenerateParams, ReturnOptions
from genai.services import ServiceInterface
from genai.utils.request_utils import match_endpoint, sanitize_params
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestServiceInterface:
    def setup_method(self):
        # mock object for the API call
        self.service = ServiceInterface(service_url="http://service_url", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def params(seld):
        return GenerateParams(decoding_method="greedy", return_options=ReturnOptions(input_text=True))

    def test_tou(self, httpx_mock: HTTPXMock):
        expected_resp = SimpleResponse.terms_of_use()
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.TOU), method="PATCH", json=expected_resp)
        resp = self.service.terms_of_use(True)

        assert resp.json() == expected_resp
        assert resp.is_success

    def test_tou_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(
            Exception("some general error"), url=match_endpoint(ServiceInterface.TOU), method="PATCH"
        )
        with pytest.raises(BaseException, match="some general error"):
            self.service.terms_of_use(True)

    def test_sanitize_params(self, params):
        new_dict = sanitize_params(params=params)

        assert isinstance(new_dict, dict)
        assert "min_new_tokens" not in new_dict
