import pytest
from pytest_httpx import HTTPXMock

from genai.schemas import GenerateParams
from genai.services import RequestHandler, ServiceInterface
from tests.utils import match_endpoint


@pytest.mark.unit
class TestRequestHandler:
    def setup_method(self):
        self.model = "somemodel"
        self.inputs = ["a"]

    @pytest.fixture
    def params(self):
        return GenerateParams(decoding_method="greedy").model_dump(by_alias=True, exclude_none=True)

    def test_metadata_post(self, params):
        headers, json_data, _ = RequestHandler._metadata(
            method="POST",
            key="API_KEY",
            model_id=self.model,
            inputs=self.inputs,
            parameters=params,
        )

        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer API_KEY"

        assert json_data == {
            "model_id": self.model,
            "inputs": self.inputs,
            "parameters": {"decoding_method": "greedy"},
        }

    def test_metadata_get(self):
        headers, _, _ = RequestHandler._metadata(method="GET", key="API_KEY")

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer API_KEY"

    def test_get(self, httpx_mock: HTTPXMock):
        expected_resp = {"some": "history"}
        params = {"limit": 1, "status": "SUCCESS"}
        httpx_mock.add_response(
            url=match_endpoint(ServiceInterface.HISTORY, query_params=params), method="GET", json=expected_resp
        )

        s = ServiceInterface(service_url="http://service_url", api_key="KEY")
        his = s.history(params=params)

        assert his.json() == expected_resp

    def test_post(self, httpx_mock: HTTPXMock):
        expected_resp = "some tokens"
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.TOKENIZE), method="POST", json=expected_resp)

        s = ServiceInterface(service_url="http://service_url", api_key="KEY")
        token = s.tokenize(model="model", inputs=["input"])

        assert token.json() == expected_resp
