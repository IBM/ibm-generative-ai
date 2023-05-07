import aiolimiter
import httpx

from genai.exceptions import GenAiException

__all__ = ["ConnectionManager"]


class ConnectionManager:
    MAX_CONCURRENT_GENERATE = 10
    MAX_RETRIES_GENERATE = 3
    TIMEOUT_GENERATE = 600
    MAX_RETRIES_TOKENIZE = 3
    MAX_REQ_PER_SECOND_TOKENIZE = 5
    TIMEOUT = 600

    generate_limits = httpx.Limits(
        max_keepalive_connections=MAX_CONCURRENT_GENERATE,
        max_connections=MAX_CONCURRENT_GENERATE,
    )
    async_generate_client = None
    async_tokenize_client = None
    async_tokenize_limiter = aiolimiter.AsyncLimiter(max_rate=MAX_REQ_PER_SECOND_TOKENIZE, time_period=1)

    @staticmethod
    def make_generate_client():
        """Function to make async httpx client for generate."""
        if ConnectionManager.async_generate_client is not None:
            raise GenAiException(ValueError("Can't have two active async_generate_clients"))
        async_generate_transport = httpx.AsyncHTTPTransport(
            limits=ConnectionManager.generate_limits, retries=ConnectionManager.MAX_RETRIES_GENERATE
        )
        ConnectionManager.async_generate_client = httpx.AsyncClient(
            transport=async_generate_transport, timeout=ConnectionManager.TIMEOUT_GENERATE
        )

    @staticmethod
    def make_tokenize_client():
        """Function to make async httpx client for tokenize."""
        if ConnectionManager.async_tokenize_client is not None:
            raise GenAiException(ValueError("Can't have two active async_tokenize_clients"))
        ConnectionManager.async_tokenize_limiter = aiolimiter.AsyncLimiter(
            max_rate=ConnectionManager.MAX_REQ_PER_SECOND_TOKENIZE, time_period=1
        )
        ConnectionManager.async_tokenize_client = httpx.AsyncClient()

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
