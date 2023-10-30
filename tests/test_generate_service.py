from unittest import TestCase

import pytest
from pydantic import ValidationError
from pytest_httpx import HTTPXMock

from genai.schemas import GenerateParams
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint


@pytest.mark.unit
class TestGenerateService:
    def setup_method(self):
        self.service = ServiceInterface(service_url="http://service_url", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def params(self):
        return GenerateParams(decoding_method="sample", max_new_tokens=5, min_new_tokens=0)

    def test_generate_with_params(self, params, httpx_mock: HTTPXMock):
        expected_resp = SimpleResponse.generate(model=self.model, inputs=self.inputs, params=params)
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=expected_resp)

        g = self.service.generate(model=self.model, inputs=self.inputs, params=params)

        assert g.is_success
        TestCase().assertDictEqual(g.json(), expected_resp)

    def test_generate_with_no_params(self, httpx_mock: HTTPXMock):
        expected_resp = SimpleResponse.generate(model=self.model, inputs=self.inputs)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=expected_resp)
        g = self.service.generate(model=self.model, inputs=self.inputs)

        assert g.is_success
        TestCase().assertDictEqual(g.json(), expected_resp)

    def test_generate_with_invalid_params(self):
        with pytest.raises(ValidationError):
            self.service.generate(
                model=self.model,
                inputs=self.inputs,
                params=GenerateParams(decoding_method="not the right method"),
            )

    def test_generate_empty_body(self):
        with pytest.raises(TypeError):
            self.service.generate()

    def test_generate_with_no_model(self):
        with pytest.raises(TypeError):
            self.service.generate(inputs=self.inputs)

    def test_generate_with_no_input(self):
        with pytest.raises(TypeError):
            self.service.generate(model=self.model)

    def test_generate_general_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(Exception("some general error"), url=match_endpoint(ServiceInterface.GENERATE))
        with pytest.raises(BaseException, match="some general error"):
            self.service.generate(model="somemodel", inputs=["inputs"])
