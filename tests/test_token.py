from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from genai.schemas import TokenParams
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate


@pytest.mark.unit
class TestTokenize:
    def setup_method(self):
        # mock object for the API call
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def request_body(self):
        return {
            "model": self.model,
            "inputs": self.inputs,
            "params": self.params,
        }

    @pytest.fixture
    def params(self):
        return TokenParams(return_tokens=True)

    @pytest.fixture
    def no_token_params(self):
        return TokenParams(return_tokens=False)

    @patch("genai.services.RequestHandler.post")
    def test_tokenize(self, mock_requests, params):
        expected_resp = SimpleResponse.tokenize(model=self.model, inputs=self.inputs, params=params)
        mock_response = MagicMock(status_code=200, json=expected_resp)

        mock_requests.return_value = mock_response
        t = self.service.tokenize(model=self.model, inputs=self.inputs, params=params)

        assert t == mock_response
        assert t.status_code == 200

    @patch("genai.services.RequestHandler.post")
    def test_no_tokens(self, mock_requests, no_token_params):
        expected_resp = SimpleResponse.tokenize(model=self.model, inputs=self.inputs, params=no_token_params)
        mock_response = MagicMock(status_code=200, json=expected_resp)

        mock_requests.return_value = mock_response
        t = self.service.tokenize(model=self.model, inputs=self.inputs, params=no_token_params)

        assert t == mock_response
        TestCase().assertDictEqual(t.json, expected_resp)

    def test_required_fields(self, request_body):
        assert "model" in request_body
        assert "inputs" in request_body

    def test_model(self, request_body):
        assert len(self.model) > 0
        assert all(isinstance(model, str) for model in self.model)

    def test_inputs(self, request_body):
        assert len(self.inputs) > 0
        assert all(isinstance(input, str) for input in self.inputs)

    def test_invalid_fields(self):
        with pytest.raises(ValidationError):
            TokenParams(return_tokens="dummy")

    @patch("genai.services.RequestHandler.post", side_effect=Exception("some general error"))
    def test_tokenize_general_exception(self, mock):
        with pytest.raises(BaseException, match="some general error"):
            self.service.tokenize(model="somemodel", inputs=["inputs"])
