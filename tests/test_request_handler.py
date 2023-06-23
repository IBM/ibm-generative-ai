from unittest.mock import MagicMock, patch

import pytest

from genai.schemas import GenerateParams
from genai.services import RequestHandler, ServiceInterface


@pytest.mark.unit
class TestRequestHandler:
    def setup_method(self):
        self.model = "somemodel"
        self.inputs = ["a"]

    @pytest.fixture
    def params(seld):
        return GenerateParams(decoding_method="greedy").dict(by_alias=True, exclude_none=True)

    def test_metadata_post(self, params):
        headers, json_data = RequestHandler._metadata(
            method="POST", key="API_KEY", model_id=self.model, inputs=self.inputs, parameters=params
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
        headers, _ = RequestHandler._metadata(method="GET", key="API_KEY")

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer API_KEY"

    @patch("httpx.Client.get")
    def test_get(self, mock: MagicMock):
        expected_resp = {"some": "history"}
        mock.return_value = expected_resp

        s = ServiceInterface(service_url="SERVICE_URL", api_key="KEY")
        his = s.history(params={"limit": 1, "status": "SUCCESS"})

        assert his == expected_resp

    @patch("httpx.Client.post")
    def test_post(self, mock: MagicMock):
        expected_resp = "some tokens"
        mock.return_value = expected_resp

        s = ServiceInterface(service_url="SERVICE_URL", api_key="KEY")
        toekn = s.tokenize(model="model", inputs=["input"])

        assert toekn == expected_resp
