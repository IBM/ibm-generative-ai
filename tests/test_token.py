from unittest import TestCase

import pytest
from pydantic import ValidationError
from pytest_httpx import HTTPXMock

from genai.schemas import TokenParams
from genai.services import ServiceInterface
from genai.utils.request_utils import match_endpoint
from tests.assets.response_helper import SimpleResponse

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate


@pytest.mark.unit
class TestTokenize:
    def setup_method(self):
        # mock object for the API call
        self.service = ServiceInterface(service_url="http://service_url", api_key="API_KEY")
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

    def test_tokenize(self, params, httpx_mock: HTTPXMock):
        expected_resp = SimpleResponse.tokenize(model=self.model, inputs=self.inputs, params=params)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.TOKENIZE), method="POST", json=expected_resp)
        t = self.service.tokenize(model=self.model, inputs=self.inputs, params=params)

        assert t.json() == expected_resp
        assert t.is_success

    def test_no_tokens(self, no_token_params, httpx_mock: HTTPXMock):
        expected_resp = SimpleResponse.tokenize(model=self.model, inputs=self.inputs, params=no_token_params)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.TOKENIZE), method="POST", json=expected_resp)
        t = self.service.tokenize(model=self.model, inputs=self.inputs, params=no_token_params)

        TestCase().assertDictEqual(t.json(), expected_resp)

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

    def test_tokenize_general_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(Exception("some general error"), url=match_endpoint(ServiceInterface.TOKENIZE))
        with pytest.raises(BaseException, match="some general error"):
            self.service.tokenize(model="somemodel", inputs=["inputs"])
