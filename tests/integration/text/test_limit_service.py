import pytest

from genai import Client
from genai._utils.shared_loop import shared_event_loop


@pytest.mark.integration
class TestLimitService:
    @pytest.mark.vcr
    def test_retrieve(self, client: Client):
        limits = client.text.generation.limit.retrieve()
        assert limits.result.concurrency.limit > 0
        assert limits.result.concurrency.remaining > 0
        assert limits.result.concurrency.remaining <= limits.result.concurrency.limit

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_aretrieve(self, client: Client):
        with shared_event_loop:
            limits = await client.text.generation.limit.aretrieve()
            assert limits.result.concurrency.limit > 0
            assert limits.result.concurrency.remaining > 0
            assert limits.result.concurrency.remaining <= limits.result.concurrency.limit
