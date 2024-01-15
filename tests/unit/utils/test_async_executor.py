import logging
from asyncio import sleep
from unittest.mock import Mock

import pytest

from genai._utils.async_executor import execute_async
from genai._utils.http_client.httpx_client import AsyncHttpxClient
from genai._utils.limiters.local_limiter import LocalLimiter
from genai._utils.limiters.shared_limiter import LoopBoundLimiter

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestAsyncExecutor:
    @pytest.fixture
    def inputs(self) -> list[str]:
        return ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    @pytest.fixture
    def http_client(self):
        return AsyncHttpxClient()

    def get_handler(self, inputs: list[str]):
        async def handler(input: str, client: AsyncHttpxClient, *_) -> str:
            assert input
            assert client

            # Sleep duration in reverse order (from slowest to fastest)
            idx = inputs.index(input)
            total = len(inputs)
            ms = (total - idx - 1) / total / 100
            await sleep(ms)

            return input

        return handler

    @pytest.mark.parametrize("concurrency_limit", range(1, 10))
    def test_resolve_in_order(self, inputs: list[str], http_client, concurrency_limit: int):
        results = list(
            execute_async(
                inputs=inputs,
                handler=self.get_handler(inputs),
                http_client=lambda: http_client,
                throw_on_error=True,
                ordered=True,
                limiters=[LoopBoundLimiter(lambda: LocalLimiter(limit=concurrency_limit))],
            )
        )
        assert results == inputs

    @pytest.mark.parametrize("concurrency_limit", range(1, 5))
    @pytest.mark.parametrize("ordered", [True, False])
    def test_correctly_stops(self, inputs: list[str], http_client, concurrency_limit: int, ordered: bool):
        async def handler(input: str, *args) -> str:
            idx = inputs.index(input)
            total = len(inputs)
            ms = idx / total / 100
            await sleep(ms)

            if input == inputs[-1]:
                raise Exception("This error should happened.")

            return input

        collected_results = []
        with pytest.raises(Exception, match="This error should happened."):
            for result in execute_async(
                inputs=inputs,
                handler=handler,
                http_client=lambda: http_client,
                throw_on_error=True,
                ordered=ordered,
                limiters=[LoopBoundLimiter(lambda: LocalLimiter(limit=concurrency_limit))],
            ):
                assert result
                collected_results.append(result)

        collected_results.sort()
        assert collected_results == inputs[0:-1]

    @pytest.mark.parametrize("ordered", [True, False])
    def test_return_none_when_throw_on_error_is_false(self, inputs: list[str], http_client, ordered: bool):
        async def handler(input: str, *args) -> str:
            if input == inputs[-1] or input == inputs[0]:
                raise Exception("This error should happened.")
            return input

        collected_results = []
        none_count = 0
        for result in execute_async(
            inputs=inputs,
            handler=handler,
            http_client=lambda: http_client,
            throw_on_error=False,
            ordered=ordered,
        ):
            if result is None:
                none_count += 1
                continue
            collected_results.append(result)

        collected_results.sort()
        assert collected_results == inputs[1:-1]
        assert none_count == 2

    def test_execute_empty_inputs(self):
        for _ in execute_async(inputs=[], handler=Mock(), http_client=Mock(), throw_on_error=True):
            ...
