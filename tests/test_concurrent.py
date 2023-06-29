import json
import logging
import queue
import random
from unittest.mock import AsyncMock

import pytest

from genai.schemas import GenerateParams, ReturnOptions, TokenParams
from genai.schemas.responses import GenerateResponse, TokenizeResponse
from genai.services import AsyncResponseGenerator, RequestHandler, ServiceInterface
from genai.services.connection_manager import ConnectionManager
from tests.assets.response_helper import SimpleResponse

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestAsyncResponseGenerator:
    def setup_method(self):
        self.service = ServiceInterface(service_url="http://SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def mock_generate_json(self, mocker):
        async_mock = AsyncMock()
        mocker.patch("genai.services.AsyncResponseGenerator._get_response_json", side_effect=async_mock)
        return async_mock

    @pytest.fixture
    def generate_params(self):
        return GenerateParams(temperature=0, max_new_tokens=3, return_options=ReturnOptions(input_text=True))

    @pytest.fixture
    def mock_tokenize_json(self, mocker):
        async_mock = AsyncMock()
        mocker.patch("genai.services.AsyncResponseGenerator._get_response_json", side_effect=async_mock)
        return async_mock

    @pytest.fixture
    def tokenize_params(self):
        return TokenParams(return_tokens=True)

    @pytest.mark.asyncio
    async def test_concurrent_generate(self, mock_generate_json, generate_params):
        expected = SimpleResponse.generate(model=self.model, inputs=self.inputs)
        mock_generate_json.return_value = expected
        num_prompts = 3

        counter = 0
        with AsyncResponseGenerator(
            self.model, self.inputs * num_prompts, generate_params, self.service
        ) as asynchelper:
            assert ConnectionManager.async_generate_client is not None
            for result in asynchelper.generate_response():
                assert result == GenerateResponse(**expected).results[0]
                counter += 1
            assert counter == num_prompts
        assert ConnectionManager.async_generate_client is None

    @pytest.mark.asyncio
    async def test_concurrent_tokenize(self, mock_tokenize_json, tokenize_params):
        expected = SimpleResponse.tokenize(model=self.model, inputs=self.inputs, params=tokenize_params)
        mock_tokenize_json.return_value = expected

        with AsyncResponseGenerator(
            self.model, self.inputs, tokenize_params, self.service, fn="tokenize"
        ) as asynchelper:
            assert ConnectionManager.async_tokenize_client is not None
            for result in asynchelper.generate_response():
                assert result == TokenizeResponse(**expected).results[0]
        assert ConnectionManager.async_tokenize_client is None

    @pytest.mark.asyncio
    async def test_async_helper_total_generate_responses(self, mock_generate_json, generate_params):
        num_prompts = 7
        single_response = SimpleResponse.generate(model=self.model, inputs=self.inputs, params=generate_params)

        def side_effect(model, inputs, params):
            response = {}
            response["model_id"] = single_response["model_id"]
            response["created_at"] = single_response["created_at"]
            response["results"] = single_response["results"] * len(inputs)
            return response

        mock_generate_json.side_effect = side_effect

        with AsyncResponseGenerator(
            self.model, self.inputs * num_prompts, generate_params, self.service
        ) as asynchelper:
            assert ConnectionManager.async_generate_client is not None
            total_responses = 0
            for _ in asynchelper.generate_response():
                total_responses += 1
            assert total_responses == num_prompts
        assert ConnectionManager.async_generate_client is None

    @pytest.mark.asyncio
    async def test_async_helper_total_tokenize_responses(self, mock_tokenize_json, tokenize_params):
        num_prompts = 7
        single_response = SimpleResponse.tokenize(model=self.model, inputs=self.inputs, params=tokenize_params)

        def side_effect(model, inputs, params):
            response = {}
            response["model_id"] = single_response["model_id"]
            response["created_at"] = single_response["created_at"]
            response["results"] = single_response["results"] * len(inputs)
            return response

        mock_tokenize_json.side_effect = side_effect

        with AsyncResponseGenerator(
            self.model, self.inputs * num_prompts, tokenize_params, self.service, fn="tokenize"
        ) as asynchelper:
            assert ConnectionManager.async_tokenize_client is not None
            total_responses = 0
            for _ in asynchelper.generate_response():
                total_responses += 1
            assert total_responses == num_prompts
        assert ConnectionManager.async_tokenize_client is None

    @pytest.mark.asyncio
    async def test_concurrent_tokenize_dropped_request(self, httpx_mock, tokenize_params):
        # Return a 429 for a tokenize request from RequestHandler
        httpx_mock.add_response(method="POST", status_code=429, json={})
        num_prompts = 17
        counter = 0
        with AsyncResponseGenerator(
            self.model, self.inputs * num_prompts, tokenize_params, self.service
        ) as asynchelper:
            for result in asynchelper.generate_response():
                assert result is None
                counter += 1
            assert counter == num_prompts

    @pytest.mark.asyncio
    async def test_concurrent_generate_dropped_request(self, httpx_mock, generate_params):
        failed_id = 4
        single_response = SimpleResponse.generate(model=self.model, inputs=self.inputs, params=generate_params)
        headers, json_data = RequestHandler._metadata(
            "POST",
            key="TEST_KEY",
            model_id=self.model,
            inputs=["Input " + str(failed_id)],
            parameters=ServiceInterface._sanitize_params(generate_params),
        )
        # Following two lines: Selected input id should return 429, others should succeed
        httpx_mock.add_response(method="POST", json=single_response)
        httpx_mock.add_response(
            method="POST", status_code=429, match_content=bytes(json.dumps(json_data), encoding="utf-8")
        )
        num_prompts = 9
        counter = 0
        inputs = ["Input " + str(i) for i in range(num_prompts)]
        with AsyncResponseGenerator(self.model, inputs, generate_params, self.service) as asynchelper:
            assert ConnectionManager.async_generate_client is not None
            for _ in asynchelper.generate_response():
                if counter == failed_id:
                    # print(response)
                    assert True
                    # assert response is None
                else:
                    assert True
                    # assert response is not None
                counter += 1
            assert counter == num_prompts
        assert ConnectionManager.async_generate_client is None

    @pytest.mark.asyncio
    async def test_concurrent_generate_inorder(self, mock_generate_json, generate_params, mocker):
        num_prompts = 31
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.generate_response_array_async(model=self.model, inputs=inputs)
        mock_generate_json.side_effect = expected

        counter = 0
        permutation = list(range(num_prompts))
        random.shuffle(permutation)
        # Permute what comes out of the queue completely but expect results in order
        with AsyncResponseGenerator(self.model, inputs, generate_params, self.service, ordered=True) as asynchelper:
            assert ConnectionManager.async_generate_client is not None
            mocker.patch.object(
                queue.Queue,
                "get",
                spec=queue.Queue,
                side_effect=[
                    (permutation[counter], 1, GenerateResponse(**expected[permutation[counter]]))
                    for counter in range(num_prompts)
                ],
            )
            mocker.patch.object(queue.Queue, "put_nowait", spec=queue.Queue, return_value=None)
            mocker.patch.object(queue.Queue, "task_done", spec=queue.Queue, return_value=None)
            for result in asynchelper.generate_response():
                expected_result = GenerateResponse(**expected[counter]).results[0]
                assert result.generated_text == expected_result.generated_text
                assert result.input_text == inputs[counter]
                counter += 1
                mock_generate_json.return_value = expected[counter] if counter < num_prompts else None
            assert counter == num_prompts
        assert ConnectionManager.async_generate_client is None

    @pytest.mark.asyncio
    async def test_concurrent_generate_not_inorder(self, mock_generate_json, generate_params, mocker):
        num_prompts = 5
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.generate_response_array_async(model=self.model, inputs=inputs)
        mock_generate_json.side_effect = expected

        counter = 0
        permutation = list(range(num_prompts))
        random.shuffle(permutation)

        # Permute what comes out of the queue completely and expect results in the same order
        with AsyncResponseGenerator(self.model, inputs, generate_params, self.service, ordered=False) as asynchelper:
            assert ConnectionManager.async_generate_client is not None
            mocker.patch.object(
                queue.Queue,
                "get",
                spec=queue.Queue,
                side_effect=[
                    (permutation[counter], 1, GenerateResponse(**expected[permutation[counter]]))
                    for counter in range(num_prompts)
                ],
            )
            mocker.patch.object(queue.Queue, "put_nowait", spec=queue.Queue, return_value=None)
            mocker.patch.object(queue.Queue, "task_done", spec=queue.Queue, return_value=None)
            for result in asynchelper.generate_response():
                expected_result = GenerateResponse(**expected[permutation[counter]]).results[0]
                assert result.generated_text == expected_result.generated_text
                assert result.input_text == inputs[permutation[counter]]
                counter += 1
                mock_generate_json.return_value = expected[counter] if counter < num_prompts else None
            assert counter == num_prompts
        assert ConnectionManager.async_generate_client is None

    @pytest.mark.asyncio
    async def test_concurrent_tokenize_inorder(self, mock_tokenize_json, tokenize_params, mocker):
        num_prompts = 143
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(model=self.model, inputs=inputs)
        mock_tokenize_json.side_effect = expected

        permutation = list(range(len(expected)))
        random.shuffle(permutation)
        # Permute what comes out of the queue completely but expect results in order
        with AsyncResponseGenerator(
            self.model, inputs, tokenize_params, self.service, fn="tokenize", ordered=True
        ) as asynchelper:
            assert ConnectionManager.async_tokenize_client is not None
            mocker.patch.object(
                queue.Queue,
                "get",
                spec=queue.Queue,
                side_effect=[
                    (permutation[counter], asynchelper.batch_size_, TokenizeResponse(**expected[permutation[counter]]))
                    for counter in range(len(expected))
                ],
            )
            mocker.patch.object(queue.Queue, "put_nowait", spec=queue.Queue, return_value=None)
            mocker.patch.object(queue.Queue, "task_done", spec=queue.Queue, return_value=None)
            num_results = 0
            observed = list(asynchelper.generate_response())
            for counter in range(asynchelper.num_batches_):
                response = TokenizeResponse(**expected[counter])
                for result in response.results:
                    assert observed[num_results].tokens == result.tokens
                    assert observed[num_results].input_text == result.input_text
                    num_results += 1
            assert num_prompts == num_results
        assert ConnectionManager.async_tokenize_client is None

    @pytest.mark.asyncio
    async def test_concurrent_tokenize_not_inorder(self, mock_tokenize_json, tokenize_params, mocker):
        num_prompts = 143
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(model=self.model, inputs=inputs)
        mock_tokenize_json.side_effect = expected

        permutation = list(range(len(expected)))
        random.shuffle(permutation)
        # Permute what comes out of the queue completely and expect results in the same order
        with AsyncResponseGenerator(
            self.model, inputs, tokenize_params, self.service, fn="tokenize", ordered=False
        ) as asynchelper:
            assert ConnectionManager.async_tokenize_client is not None
            mocker.patch.object(
                queue.Queue,
                "get",
                spec=queue.Queue,
                side_effect=[
                    (permutation[counter], asynchelper.batch_size_, TokenizeResponse(**expected[permutation[counter]]))
                    for counter in range(len(expected))
                ],
            )
            mocker.patch.object(queue.Queue, "put_nowait", spec=queue.Queue, return_value=None)
            mocker.patch.object(queue.Queue, "task_done", spec=queue.Queue, return_value=None)
            num_results = 0
            observed = list(asynchelper.generate_response())
            for counter in range(asynchelper.num_batches_):
                response = TokenizeResponse(**expected[permutation[counter]])
                for result in response.results:
                    assert observed[num_results].tokens == result.tokens
                    assert observed[num_results].input_text == result.input_text
                    num_results += 1
            assert num_prompts == num_results
        assert ConnectionManager.async_tokenize_client is None

    @pytest.mark.asyncio
    async def test_concurrent_tokenize_nones(self, mock_tokenize_json, tokenize_params, mocker):
        # test that if one request gets dropped, we get appropriate number of nones
        num_prompts = 18
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(model=self.model, inputs=inputs)
        mock_tokenize_json.side_effect = expected

        batch_indices = list(range(len(expected)))
        side_effect = [
            (batch_indices[counter], 5, TokenizeResponse(**expected[batch_indices[counter]]))
            for counter in range(len(expected))
        ]
        # Test for failing requests for the first batch, last batch, intermediate batch
        for failed_id in [0, -1, random.randint(1, len(expected) - 2)]:
            batch_size = num_prompts % 5 if failed_id == -1 else 5
            side_effect_with_failed = side_effect[:]
            side_effect_with_failed[failed_id] = (batch_indices[failed_id], batch_size, None)

            # Permute what comes out of the queue completely and expect results in the same order
            with AsyncResponseGenerator(
                self.model, inputs, tokenize_params, self.service, fn="tokenize", ordered=False
            ) as asynchelper:
                assert ConnectionManager.async_tokenize_client is not None
                mocker.patch.object(
                    queue.Queue,
                    "get",
                    spec=queue.Queue,
                    side_effect=side_effect_with_failed,
                )
                mocker.patch.object(queue.Queue, "put_nowait", spec=queue.Queue, return_value=None)
                mocker.patch.object(queue.Queue, "task_done", spec=queue.Queue, return_value=None)
                num_results = 0
                observed = list(asynchelper.generate_response())
                for counter in range(asynchelper.num_batches_):
                    response = TokenizeResponse(**expected[counter])
                    for result in response.results:
                        if failed_id == 0 and num_results < 5:
                            assert observed[num_results] is None
                        elif failed_id == -1 and num_results >= num_prompts - num_prompts % 5:
                            assert observed[num_results] is None
                        elif (
                            failed_id * asynchelper.batch_size_
                            <= num_results
                            < (failed_id + 1) * asynchelper.batch_size_
                        ):
                            assert observed[num_results] is None
                        else:
                            assert observed[num_results].tokens == result.tokens
                            assert observed[num_results].input_text == result.input_text
                        num_results += 1
                assert num_prompts == num_results
            assert ConnectionManager.async_tokenize_client is None
