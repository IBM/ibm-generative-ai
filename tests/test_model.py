from unittest.mock import MagicMock, patch

import pytest

from genai import Credentials, Model
from genai.exceptions import GenAiException
from genai.schemas import GenerateParams, ModelType
from genai.schemas.responses import GenerateResponse, TokenizeResponse
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestModel:
    def setup_method(self):
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def credentials(self):
        return Credentials("GENAI_APY_KEY")

    @pytest.fixture
    def params(self):
        return GenerateParams(
            decoding_method="sample",
            max_new_tokens=1,
            min_new_tokens=1,
            stream=False,
            temperature=0.7,
            top_k=50,
            top_p=1,
        )

    @pytest.fixture
    def prompts(self):
        return ["a", "b", "c", "d", "e"]

    @patch("genai.services.RequestHandler.post")
    def test_generate(self, mocked_post_request, credentials, params, prompts):
        """Tests that we can call the generate endpoint"""

        GENERATE_RESPONSE = SimpleResponse.generate(model=ModelType.FLAN_UL2, inputs=prompts, params=params)
        expected_generated_response = GenerateResponse(**GENERATE_RESPONSE)

        response = MagicMock(status_code=200)
        response.json.return_value = GENERATE_RESPONSE
        mocked_post_request.return_value = response

        model = Model(ModelType.FLAN_UL2, params=params, credentials=credentials)

        responses = model.generate_as_completed(prompts=prompts)
        responses_list = list(responses)

        assert responses_list == expected_generated_response.results
        for i, response in enumerate(responses_list):
            assert response.input_text == prompts[i]

    @patch("genai.services.RequestHandler.post")
    def test_generate_throws_exception_for_non_200(self, mock_service_generate, credentials, params, prompts):
        """Tests that the GenAiException is thrown if the status code is not 200"""

        mock_service_generate.return_value = MagicMock(status_code=500)

        model = Model(ModelType.FLAN_UL2, params=params, credentials=credentials)

        with pytest.raises(GenAiException):
            model.generate(prompts=prompts)

    @patch("genai.services.RequestHandler.post", side_effect=Exception("some general error"))
    def test_generate_throws_exception_for_generic_exception(self, credentials, params, prompts):
        """Tests that the GenAiException is thrown if a generic Exception is raised"""
        model = Model(ModelType.FLAN_UL2, params=params, credentials=credentials)

        with pytest.raises(GenAiException, match="some general error"):
            model.generate(prompts=prompts)

    @patch("genai.services.RequestHandler.post")
    def test_tokenize(self, mocked_post_request, credentials, params):
        """Tests that we can call the tokenize endpoint"""

        TOKENIZE_RESPONSE = SimpleResponse.tokenize(model=ModelType.FLAN_UL2, inputs=["a", "b", "c"])
        expected_token_response = TokenizeResponse(**TOKENIZE_RESPONSE)

        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = TOKENIZE_RESPONSE
        mocked_post_request.return_value = mock_response

        model = Model(ModelType.FLAN_UL2, params=params, credentials=credentials)

        responses = model.tokenize(["a", "b", "c"], False)

        assert responses == expected_token_response.results
