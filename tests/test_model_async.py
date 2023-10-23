import re
import signal
from contextlib import nullcontext as does_not_raise
from unittest.mock import AsyncMock

import httpx
import pytest
from pytest_httpx import HTTPXMock

from genai import Credentials, Model
from genai.exceptions import GenAiException
from genai.schemas import GenerateParams, TokenParams
from genai.schemas.responses import GenerateResponse, GenerateResult, TokenizeResponse
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
        mocker.patch(
            "genai.services.AsyncResponseGenerator._get_response_json",
            side_effect=async_mock,
        )
        return async_mock

    @pytest.fixture
    def generate_params(self):
        return GenerateParams(decoding_method="sample", max_new_tokens=5, min_new_tokens=0)

    @pytest.fixture
    def mock_tokenize_json(self, mocker):
        async_mock = AsyncMock()
        mocker.patch(
            "genai.services.AsyncResponseGenerator._get_response_json",
            side_effect=async_mock,
        )
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

        model = Model(
            "google/flan-ul2",
            params=generate_params,
            credentials=creds,
        )

        counter = 0
        responses = list(model.generate_async(prompts, throw_on_error=True, hide_progressbar=True))
        assert len(responses) == len(expected)
        for batch_idx in range(len(expected)):
            for result in GenerateResponse(**expected[batch_idx]).results:
                assert responses[counter] == result
                assert prompts[counter] == result.input_text
                counter += 1
        assert counter == num_prompts

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "max_concurrency_limit,expectation,patch_generate_limits",
        [
            (1, does_not_raise(), {"tokens_capacity": 10}),
            (2, pytest.raises(AssertionError), {"tokens_capacity": 10}),
            (3, pytest.raises(AssertionError), {"tokens_capacity": 10}),
            (4, pytest.raises(AssertionError), {"tokens_capacity": 10}),
        ],
        indirect=["patch_generate_limits"],
    )
    async def test_generate_custom_concurrency_limit(
        self, generate_params, httpx_mock: HTTPXMock, max_concurrency_limit: int, expectation, patch_generate_limits
    ):
        generate_request_url = re.compile(f".+{ServiceInterface.GENERATE}$")

        num_prompts = 10
        prompts = ["TEST_PROMPT"] * num_prompts
        for prompt in prompts:
            response = SimpleResponse.generate(model=self.model, inputs=[prompt], params=generate_params)
            httpx_mock.add_response(url=generate_request_url, method="POST", json=response)

        model = Model(
            "google/flan-ul2",
            params=generate_params,
            credentials=Credentials("TEST_API_KEY"),
        )

        with expectation:
            for count, response in enumerate(
                model.generate_async(
                    prompts=prompts,
                    max_concurrency_limit=max_concurrency_limit,
                    throw_on_error=True,
                    hide_progressbar=True,
                    ordered=False,
                ),
                start=1,
            ):
                assert len(httpx_mock.get_requests(url=generate_request_url)) == count
                assert response is not None

    @pytest.mark.asyncio
    async def test_tokenize_async(self, mock_tokenize_json, tokenize_params):
        num_prompts = 31
        prompts = ["TEST_PROMPT " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(
            model=self.model, inputs=prompts, params=tokenize_params
        )
        creds = Credentials("TEST_API_KEY")
        mock_tokenize_json.side_effect = expected

        model = Model("google/flan-ul2", params=tokenize_params, credentials=creds)

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
        model = Model("google/flan-ul2", params=generate_params, credentials=creds)

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
        model = Model("google/flan-ul2", params=tokenize_params, credentials=creds)

        for result in model.tokenize_async(prompts, callback=tasks_completed):
            pass

        assert message == TokenizeResponse(**expected[0]).results[0].tokens * num_prompts

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "patch_generate_limits",
        [
            ({"tokens_capacity": 1}),
        ],
        indirect=["patch_generate_limits"],
    )
    async def test_generate_async_progress_bar(
        self, generate_params, patch_async_requests_limits, patch_generate_limits, httpx_mock: HTTPXMock
    ):
        """Tests that the response is yielded immediately (key part for the progress bar to work as expected)"""
        handled_responses = 0

        def handle_request(request: httpx.Request):
            nonlocal handled_responses
            handled_responses += 1

            return httpx.Response(json=SimpleResponse.generate(inputs=["Hello"], model=self.model), status_code=200)

        httpx_mock.add_callback(
            callback=handle_request,
            url=re.compile(f".+{ServiceInterface.GENERATE}$"),
            method="POST",
        )

        model = Model(self.model, params=generate_params, credentials=Credentials("TEST_API_KEY"))
        prompts = ["Hello world!"] * 10

        for count, response in enumerate(
            model.generate_async(prompts=prompts, hide_progressbar=True, throw_on_error=True),
            start=1,
        ):
            assert count == handled_responses
            assert response is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("throw_in_callback", [True, False])
    @pytest.mark.parametrize("termination_signal", [signal.SIGINT, signal.SIGTERM])
    @pytest.mark.parametrize("execution_params", [{"throw_on_error": True}, {"throw_on_error": False}])
    async def test_generate_termination_results(
        self,
        generate_params,
        httpx_mock: HTTPXMock,
        execution_params: dict,
        throw_in_callback: bool,
        termination_signal: int,
    ):
        """Tests that the processing in case of crash ends up as soon as possible"""
        url = re.compile(f".+{ServiceInterface.GENERATE}$")
        httpx_mock.add_response(
            url=url,
            method="POST",
            json=SimpleResponse.generate(model=self.model, inputs=self.inputs),
        )

        model = Model(self.model, params=generate_params, credentials=Credentials("TEST_API_KEY"))
        prompts = ["Hello world!"] * 10
        chunk_size = 5
        has_raised = False

        def callback(result: GenerateResult):
            assert result is not None
            nonlocal has_raised
            if throw_in_callback and not has_raised:
                has_raised = True
                raise GenAiException("Unexpected Callback Error")

        with pytest.raises(GenAiException):
            for response in enumerate(
                model.generate_async(
                    **execution_params,
                    prompts=prompts,
                    hide_progressbar=True,
                    max_concurrency_limit=chunk_size,
                    callback=callback,
                ),
            ):
                assert response is not None
                # Abort as soon as possible
                if not has_raised and not throw_in_callback:
                    has_raised = True
                    signal.raise_signal(termination_signal)

        # Only one chunk is completed and then the process is terminated
        requests = httpx_mock.get_requests(url=url, method="POST")
        assert len(requests) == chunk_size
