import aiolimiter
from aiolimiter import AsyncLimiter
from httpx import AsyncClient

from genai.exceptions import GenAiException

__all__ = ["ConnectionManager"]

from genai.utils.http_provider import HttpProvider


class ConnectionManager:
    MAX_RETRIES_GENERATE = 3
    TIMEOUT_GENERATE = 600
    MAX_RETRIES_TOKENIZE = 3
    MAX_REQ_PER_SECOND_TOKENIZE = 10
    TIMEOUT = 600

    async_generate_client: AsyncClient = None
    async_tokenize_client: AsyncClient = None
    async_tokenize_limiter: AsyncLimiter = None

    @staticmethod
    def make_generate_client():
        """Function to make async httpx client for generate."""
        if ConnectionManager.async_generate_client is not None:
            raise GenAiException(ValueError("Can't have two active async_generate_clients"))

        async_generate_transport = HttpProvider.get_async_transport(
            retries=ConnectionManager.MAX_RETRIES_GENERATE,
        )
        ConnectionManager.async_generate_client = HttpProvider.get_async_client(
            transport=async_generate_transport,
            timeout=ConnectionManager.TIMEOUT_GENERATE,
        )

    @staticmethod
    def make_tokenize_client():
        """Function to make async httpx client for tokenize."""
        if ConnectionManager.async_tokenize_client is not None:
            raise GenAiException(ValueError("Can't have two active async_tokenize_clients"))

        ConnectionManager.async_tokenize_limiter = aiolimiter.AsyncLimiter(
            max_rate=ConnectionManager.MAX_REQ_PER_SECOND_TOKENIZE, time_period=1
        )
        ConnectionManager.async_tokenize_client = HttpProvider.get_async_client()

    @staticmethod
    async def delete_generate_client():
        """Function to delete async httpx client for generate."""
        if ConnectionManager.async_generate_client is not None:
            await ConnectionManager.async_generate_client.aclose()
            ConnectionManager.async_generate_client = None

    @staticmethod
    async def delete_tokenize_client():
        """Function to delte async httpx client for tokenize."""
        if ConnectionManager.async_tokenize_client is not None:
            await ConnectionManager.async_tokenize_client.aclose()
            ConnectionManager.async_tokenize_client = None
