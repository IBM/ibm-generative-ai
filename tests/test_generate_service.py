from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from genai.schemas import GenerateParams
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestGenerateService:
    def setup_method(self):
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def params(self):
        return GenerateParams(decoding_method="sample", max_new_tokens=5, min_new_tokens=0)

    @patch("genai.services.RequestHandler.post")
    def test_generate_with_params(self, mocked_post_request: MagicMock, params):
        expected_resp = SimpleResponse.generate(model=self.model, inputs=self.inputs, params=params)
        expected = MagicMock(status_code=200, json=expected_resp)

        mocked_post_request.return_value = expected
        g = self.service.generate(model=self.model, inputs=self.inputs, params=params)

        assert g == expected
        assert g.status_code == 200
        TestCase().assertDictEqual(g.json, expected_resp)

    @patch("genai.services.RequestHandler.post")
    def test_generate_with_no_params(self, mocked_post_request):
        expected_resp = SimpleResponse.generate(model=self.model, inputs=self.inputs)
        expected = MagicMock(status_code=200, json=expected_resp)

        mocked_post_request.return_value = expected
        g = self.service.generate(model=self.model, inputs=self.inputs)

        assert g == expected
        assert g.status_code == 200
        TestCase().assertDictEqual(g.json, expected_resp)

    def test_generate_with_invalid_params(self):
        with pytest.raises(ValidationError):
            self.service.generate(
                model=self.model, inputs=self.inputs, params=GenerateParams(decoding_method="not the right method")
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

    @patch("genai.services.RequestHandler.post", side_effect=Exception("some general error"))
    def test_generate_general_exception(self, mock):
        with pytest.raises(BaseException, match="some general error"):
            self.service.generate(model="somemodel", inputs=["inputs"])
