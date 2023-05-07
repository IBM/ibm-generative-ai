from unittest.mock import AsyncMock

import pytest

from genai import Credentials, Model
from genai.schemas import GenerateParams, ModelType, TokenParams
from genai.schemas.responses import GenerateResponse, TokenizeResponse
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestModelAsync:
    def setup_method(self):
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def mock_generate_json(self, mocker):
        async_mock = AsyncMock()
        mocker.patch("genai.services.AsyncResponseGenerator._get_response_json", side_effect=async_mock)
        return async_mock

    @pytest.fixture
    def generate_params(self):
        return GenerateParams(decoding_method="sample", max_new_tokens=5, min_new_tokens=0)

    @pytest.fixture
    def mock_tokenize_json(self, mocker):
        async_mock = AsyncMock()
        mocker.patch("genai.services.AsyncResponseGenerator._get_response_json", side_effect=async_mock)
        return async_mock

    @pytest.fixture
    def tokenize_params(self):
        return TokenParams(return_tokens=True)

    @pytest.mark.asyncio
    async def test_generate_async(self, mock_generate_json, generate_params):
        num_prompts = 31
        prompts = ["TEST_PROMPT"] * num_prompts
        expected = SimpleResponse.generate_response_array_async(
            model=self.model, inputs=prompts, params=generate_params
        )
        creds = Credentials("TEST_API_KEY")
        mock_generate_json.side_effect = expected

        model = Model(ModelType.FLAN_UL2, params=generate_params, credentials=creds)

        counter = 0
        responses = list(model.generate_async(prompts))
        for batch_idx in range(len(expected)):
            for result in GenerateResponse(**expected[batch_idx]).results:
                assert responses[counter] == result
                assert prompts[counter] == result.input_text
                counter += 1
        assert counter == num_prompts

    @pytest.mark.asyncio
    async def test_tokenize_async(self, mock_tokenize_json, tokenize_params):
        num_prompts = 31
        prompts = ["TEST_PROMPT " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(
            model=self.model, inputs=prompts, params=tokenize_params
        )
        creds = Credentials("TEST_API_KEY")
        mock_tokenize_json.side_effect = expected

        model = Model(ModelType.FLAN_UL2, params=tokenize_params, credentials=creds)

        counter = 0
        responses = list(model.tokenize_async(prompts))
        for batch_idx in range(len(expected)):
            for result in TokenizeResponse(**expected[batch_idx]).results:
                assert responses[counter] == result
                assert prompts[counter] == result.input_text
                counter += 1
        assert counter == num_prompts

    @pytest.mark.asyncio
    async def test_generate_callback(self, mock_generate_json, generate_params):
        num_prompts = 41
        single_response = SimpleResponse.generate(model=self.model, inputs=self.inputs, params=generate_params)
        creds = Credentials("TEST_API_KEY")
        mock_generate_json.return_value = single_response

        message = ""

        def tasks_completed(result):
            nonlocal message
            message += result.generated_text

        prompts = ["TEST_PROMPT"] * num_prompts
        model = Model(ModelType.FLAN_UL2, params=generate_params, credentials=creds)

        for result in model.generate_async(prompts, callback=tasks_completed):
            pass

        assert message == GenerateResponse(**single_response).results[0].generated_text * num_prompts

    @pytest.mark.asyncio
    async def test_tokenize_callback(self, mock_tokenize_json, tokenize_params):
        num_prompts = 29
        inputs = ["Input input" for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(model=self.model, inputs=inputs, params=tokenize_params)
        creds = Credentials("TEST_API_KEY")
        mock_tokenize_json.side_effect = expected

        message = []

        def tasks_completed(result):
            nonlocal message
            message += result.tokens

        prompts = ["TEST_PROMPT"] * num_prompts
        model = Model(ModelType.FLAN_UL2, params=tokenize_params, credentials=creds)

        for result in model.tokenize_async(prompts, callback=tasks_completed):
            pass

        assert message == TokenizeResponse(**expected[0]).results[0].tokens * num_prompts
