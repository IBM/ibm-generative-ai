import json
import logging
import queue
import random
import time
from unittest.mock import patch

import httpx
import pytest
from pytest_httpx import HTTPXMock

from genai.exceptions import GenAiException
from genai.schemas import GenerateParams, ReturnOptions, TokenParams
from genai.schemas.responses import GenerateResponse, TokenizeResponse
from genai.services import AsyncResponseGenerator, RequestHandler, ServiceInterface
from genai.services.connection_manager import ConnectionManager
from genai.utils.request_utils import sanitize_params
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestAsyncResponseGenerator:
    def setup_method(self):
        self.service = ServiceInterface(service_url="http://SERVICE_URL", api_key="API_KEY")
        self.model = "google/flan-ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def generate_params(self):
        return GenerateParams(
            temperature=0.05,
            max_new_tokens=3,
            return_options=ReturnOptions(input_text=True),
        )

    @pytest.fixture
    def tokenize_params(self):
        return TokenParams(return_tokens=True)

    @pytest.mark.asyncio
    async def test_concurrent_generate(self, generate_params, httpx_mock: HTTPXMock):
        expected = SimpleResponse.generate(model=self.model, inputs=self.inputs)

        httpx_mock.add_response(url=match_endpoint(self.service.GENERATE), method="POST", json=expected)
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
    async def test_concurrent_tokenize(self, tokenize_params, httpx_mock: HTTPXMock):
        expected = SimpleResponse.tokenize(model=self.model, inputs=self.inputs, params=tokenize_params)

        httpx_mock.add_response(url=match_endpoint(self.service.TOKENIZE), method="POST", json=expected)

        with AsyncResponseGenerator(
            self.model, self.inputs, tokenize_params, self.service, fn="tokenize"
        ) as asynchelper:
            assert ConnectionManager.async_tokenize_client is not None
            for result in asynchelper.generate_response():
                assert result == TokenizeResponse(**expected).results[0]
        assert ConnectionManager.async_tokenize_client is None

    @pytest.mark.asyncio
    async def test_async_helper_total_generate_responses(self, generate_params, httpx_mock: HTTPXMock):
        num_prompts = 7
        single_response = SimpleResponse.generate(model=self.model, inputs=self.inputs, params=generate_params)

        httpx_mock.add_response(url=match_endpoint(self.service.GENERATE), method="POST", json=single_response)

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
    async def test_async_helper_total_tokenize_responses(self, tokenize_params, httpx_mock: HTTPXMock):
        num_prompts = 7
        single_response = SimpleResponse.tokenize(model=self.model, inputs=self.inputs, params=tokenize_params)
        single_response["results"] = single_response["results"] * num_prompts

        httpx_mock.add_response(url=match_endpoint(self.service.TOKENIZE), method="POST", json=single_response)

        with AsyncResponseGenerator(
            self.model,
            self.inputs * num_prompts,
            tokenize_params,
            self.service,
            fn="tokenize",
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
        httpx_mock.add_response(url=match_endpoint(self.service.TOKENIZE), method="POST", status_code=429, json={})
        num_prompts = 17
        counter = 0
        with AsyncResponseGenerator(
            self.model,
            self.inputs * num_prompts,
            tokenize_params,
            self.service,
            fn="tokenize",
        ) as asynchelper:
            for result in asynchelper.generate_response():
                assert result is None
                counter += 1
            assert counter == num_prompts

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="pytest_httpx does not handle custom transports")
    async def test_concurrent_generate_retry(self, httpx_mock: HTTPXMock, generate_params):
        with patch.multiple(AsyncResponseGenerator, MAX_RETRIES_GENERATE=1):
            for code in [httpx.codes.SERVICE_UNAVAILABLE, httpx.codes.TOO_MANY_REQUESTS]:
                httpx_mock.add_response(method="POST", status_code=code, json={})
                httpx_mock.add_response(method="POST", status_code=httpx.codes.OK, json={})

                with AsyncResponseGenerator(self.model, self.inputs, generate_params, self.service) as asynchelper:
                    response = list(asynchelper.generate_response())
                    assert len(response) == 2
                    assert response[0] is None
                    assert response[1] is not None

                requests = httpx_mock.get_requests(url=match_endpoint(ServiceInterface.GENERATE), method="POST")
                assert len(requests) == 2

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="pytest_httpx does not handle custom transports")
    async def test_concurrent_tokenize_retry(self, httpx_mock: HTTPXMock, tokenize_params):
        saved = ConnectionManager.MAX_RETRIES_TOKENIZE
        ConnectionManager.MAX_RETRIES_TOKENIZE = 2
        for code in [httpx.codes.SERVICE_UNAVAILABLE, httpx.codes.TOO_MANY_REQUESTS]:
            httpx_mock.add_response(method="POST", status_code=code, json={})
            with AsyncResponseGenerator(
                self.model, self.inputs, tokenize_params, self.service, fn="tokenize"
            ) as asynchelper:
                time_start = time.time()
                for result in asynchelper.generate_response():
                    assert result is None
                time_end = time.time()
                assert time_end - time_start > 5
        ConnectionManager.MAX_RETRIES_TOKENIZE = saved

    @pytest.mark.asyncio
    async def test_concurrent_generate_dropped_request(self, httpx_mock: HTTPXMock, generate_params):
        failed_id = 4
        single_response = SimpleResponse.generate(model=self.model, inputs=self.inputs, params=generate_params)
        headers, json_data, _ = RequestHandler._metadata(
            "POST",
            key="TEST_KEY",
            model_id=self.model,
            inputs=["Input " + str(failed_id)],
            parameters=sanitize_params(generate_params),
        )
        # Following two lines: Selected input id should return 429, others should succeed
        httpx_mock.add_response(url=match_endpoint(self.service.GENERATE), method="POST", json=single_response)
        httpx_mock.add_response(
            url=match_endpoint(self.service.GENERATE),
            method="POST",
            status_code=429,
            match_content=bytes(json.dumps(json_data), encoding="utf-8"),
        )
        num_prompts = 9
        counter = 0
        inputs = ["Input " + str(i) for i in range(num_prompts)]
        with AsyncResponseGenerator(self.model, inputs, generate_params, self.service) as asynchelper:
            assert ConnectionManager.async_generate_client is not None
            for response in asynchelper.generate_response():
                if counter == failed_id:
                    assert response is None
                else:
                    assert response is not None
                counter += 1
            assert counter == num_prompts
        assert ConnectionManager.async_generate_client is None

    @pytest.mark.asyncio
    async def test_concurrent_generate_inorder(self, generate_params, mocker, httpx_mock: HTTPXMock):
        num_prompts = 31
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.generate_response_array_async(model=self.model, inputs=inputs)

        for response in expected:
            httpx_mock.add_response(url=match_endpoint(self.service.GENERATE), method="POST", json=response)

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
                    (
                        permutation[counter],
                        1,
                        GenerateResponse(**expected[permutation[counter]]),
                        None,
                    )
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
            assert counter == num_prompts
        assert ConnectionManager.async_generate_client is None

    @pytest.mark.asyncio
    async def test_concurrent_generate_not_inorder(self, generate_params, mocker, httpx_mock: HTTPXMock):
        num_prompts = 5
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.generate_response_array_async(model=self.model, inputs=inputs)

        for response in expected:
            httpx_mock.add_response(url=match_endpoint(self.service.GENERATE), method="POST", json=response)

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
                    (
                        permutation[counter],
                        1,
                        GenerateResponse(**expected[permutation[counter]]),
                        None,
                    )
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
            assert counter == num_prompts
        assert ConnectionManager.async_generate_client is None

    @pytest.mark.asyncio
    async def test_concurrent_tokenize_inorder(self, tokenize_params, mocker, httpx_mock: HTTPXMock):
        num_prompts = 143
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(model=self.model, inputs=inputs)

        for response in expected:
            httpx_mock.add_response(url=match_endpoint(self.service.TOKENIZE), method="POST", json=response)

        permutation = list(range(len(expected)))
        random.shuffle(permutation)
        # Permute what comes out of the queue completely but expect results in order
        with AsyncResponseGenerator(
            self.model,
            inputs,
            tokenize_params,
            self.service,
            fn="tokenize",
            ordered=True,
        ) as asynchelper:
            assert ConnectionManager.async_tokenize_client is not None
            mocker.patch.object(
                queue.Queue,
                "get",
                spec=queue.Queue,
                side_effect=[
                    (
                        permutation[counter],
                        asynchelper._batch_size,
                        TokenizeResponse(**expected[permutation[counter]]),
                        None,
                    )
                    for counter in range(len(expected))
                ],
            )
            mocker.patch.object(queue.Queue, "put_nowait", spec=queue.Queue, return_value=None)
            mocker.patch.object(queue.Queue, "task_done", spec=queue.Queue, return_value=None)
            num_results = 0
            observed = list(asynchelper.generate_response())
            for counter in range(asynchelper._num_batches):
                response = TokenizeResponse(**expected[counter])
                for result in response.results:
                    assert observed[num_results].tokens == result.tokens
                    assert observed[num_results].input_text == result.input_text
                    num_results += 1
            assert num_prompts == num_results
        assert ConnectionManager.async_tokenize_client is None

    @pytest.mark.asyncio
    async def test_concurrent_tokenize_not_inorder(self, tokenize_params, mocker, httpx_mock):
        num_prompts = 143
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(model=self.model, inputs=inputs)

        for response in expected:
            httpx_mock.add_response(url=match_endpoint(self.service.TOKENIZE), method="POST", json=response)

        permutation = list(range(len(expected)))
        random.shuffle(permutation)
        # Permute what comes out of the queue completely and expect results in the same order
        with AsyncResponseGenerator(
            self.model,
            inputs,
            tokenize_params,
            self.service,
            fn="tokenize",
            ordered=False,
        ) as asynchelper:
            assert ConnectionManager.async_tokenize_client is not None
            mocker.patch.object(
                queue.Queue,
                "get",
                spec=queue.Queue,
                side_effect=[
                    (
                        permutation[counter],
                        asynchelper._batch_size,
                        TokenizeResponse(**expected[permutation[counter]]),
                        None,
                    )
                    for counter in range(len(expected))
                ],
            )
            mocker.patch.object(queue.Queue, "put_nowait", spec=queue.Queue, return_value=None)
            mocker.patch.object(queue.Queue, "task_done", spec=queue.Queue, return_value=None)
            num_results = 0
            observed = list(asynchelper.generate_response())
            for counter in range(asynchelper._num_batches):
                response = TokenizeResponse(**expected[permutation[counter]])
                for result in response.results:
                    assert observed[num_results].tokens == result.tokens
                    assert observed[num_results].input_text == result.input_text
                    num_results += 1
            assert num_prompts == num_results
        assert ConnectionManager.async_tokenize_client is None

    @pytest.mark.asyncio
    async def test_concurrent_tokenize_nones(self, tokenize_params, mocker, httpx_mock: HTTPXMock):
        # test that if one request gets dropped, we get appropriate number of nones
        num_prompts = 18
        inputs = ["This is input number " + str(i) for i in range(num_prompts)]
        expected = SimpleResponse.tokenize_response_array_async(model=self.model, inputs=inputs)

        for response in expected:
            httpx_mock.add_response(url=match_endpoint(self.service.TOKENIZE), method="POST", json=response)

        batch_indices = list(range(len(expected)))
        side_effect = [
            (
                batch_indices[counter],
                5,
                TokenizeResponse(**expected[batch_indices[counter]]),
                None,
            )
            for counter in range(len(expected))
        ]
        # Test for failing requests for the first batch, last batch, intermediate batch
        for failed_id in [0, -1, random.randint(1, len(expected) - 2)]:
            batch_size = num_prompts % 5 if failed_id == -1 else 5
            side_effect_with_failed = side_effect[:]
            side_effect_with_failed[failed_id] = (
                batch_indices[failed_id],
                batch_size,
                None,
                GenAiException("Something went wrong!"),
            )

            # Permute what comes out of the queue completely and expect results in the same order
            with AsyncResponseGenerator(
                self.model,
                inputs,
                tokenize_params,
                self.service,
                fn="tokenize",
                ordered=False,
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
                for counter in range(asynchelper._num_batches):
                    response = TokenizeResponse(**expected[counter])
                    for result in response.results:
                        if failed_id == 0 and num_results < 5:
                            assert observed[num_results] is None
                        elif failed_id == -1 and num_results >= num_prompts - num_prompts % 5:
                            assert observed[num_results] is None
                        elif (
                            failed_id * asynchelper._batch_size
                            <= num_results
                            < (failed_id + 1) * asynchelper._batch_size
                        ):
                            assert observed[num_results] is None
                        else:
                            assert observed[num_results].tokens == result.tokens
                            assert observed[num_results].input_text == result.input_text
                        num_results += 1
                assert num_prompts == num_results
            assert ConnectionManager.async_tokenize_client is None
