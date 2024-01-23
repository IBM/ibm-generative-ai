from asyncio import AbstractEventLoop
from typing import Any, Optional

from httpx import Timeout
from pydantic import BaseModel, ConfigDict, Field, field_validator

from genai._types import ModelLike
from genai._utils.general import hash_params, merge_objects, to_model_instance
from genai._utils.http_client.httpx_client import (
    AsyncHttpxClient,
    HttpxClient,
    ReusableAsyncHttpxClient,
)
from genai._utils.http_client.rate_limit_transport import AsyncRateLimitTransport
from genai._utils.http_client.retry_transport import AsyncRetryTransport, RetryTransport
from genai._utils.shared_loop import shared_event_loop
from genai._version import __version__
from genai.credentials import Credentials

__all__ = ["HttpClientOptions", "HttpTransportOptions", "BaseConfig"]


class HttpClientOptions(BaseModel):
    """Options for httpx client"""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    timeout: Timeout = Timeout(timeout=10 * 60, connect=10)

    @field_validator("timeout", mode="before")
    @classmethod
    def check_timeout(cls, timeout: Any):
        if isinstance(timeout, dict):
            return Timeout(**timeout)
        elif isinstance(timeout, int) or isinstance(timeout, float):
            return Timeout(timeout=timeout, connect=10)

        return timeout


class HttpTransportOptions(BaseModel, extra="allow"):
    """Options for httpx transports"""

    retries: int = 3
    retry_status_codes: Optional[list[int]] = None
    backoff_factor: float = 0.2


class BaseConfig(BaseModel, extra="forbid"):
    """Default configuration for ApiClient"""

    client_options: HttpClientOptions = HttpClientOptions()
    transport_options: HttpTransportOptions = HttpTransportOptions()
    max_payload_size_bytes: int = Field(
        1024**2 // 2,  # 0.5 MiB
        description="Max payload size of body payload which API can process.",
    )


class ApiClient:
    """
    Class which provides methods for making API requests.
    It provides methods for obtaining synchronous and asynchronous HTTP clients.
    """

    Config: type[BaseConfig] = BaseConfig

    def __init__(self, *, credentials: Credentials, config: Optional[ModelLike[BaseConfig]] = None):
        self.config = to_model_instance(config, ApiClient.Config)
        self._credentials = credentials
        self._async_http_clients: dict[str, ReusableAsyncHttpxClient] = {}
        self._latest_event_loop: Optional[AbstractEventLoop] = None

    def get_http_client(self, retry_options: Optional[dict] = None, **kwargs) -> HttpxClient:
        return HttpxClient(
            **self._get_client_options(kwargs),
            transport=RetryTransport(**self._get_transport_options(override=retry_options)),
        )

    def get_async_http_client(
        self,
        rate_limit_options: Optional[dict] = None,
        retry_options: Optional[dict] = None,
        client_options: Optional[dict] = None,
        **kwargs,
    ) -> AsyncHttpxClient:
        """
        Gets cached instance of AsyncHttpxClient (cache key is created from provided parameters).

        Raises:
            ValueError: If both rate_limit_options and retry_options are provided.
            RuntimeError: If the method is not called within an asynchronous environment.
        """
        if rate_limit_options and retry_options:
            raise ValueError("Cannot pass both 'rate_limit_options' and 'retry_options' parameters.")

        loop = shared_event_loop.get_running_loop()
        if loop is None:
            raise RuntimeError("Async HTTP Client must be retrieved within async environment.")

        if self._latest_event_loop is not loop:
            self._async_http_clients.clear()
            self._latest_event_loop = loop

        params_hash = hash_params(
            rate_limit_options=rate_limit_options,
            retry_options=retry_options,
            client_options=client_options,
            **kwargs,
        )

        if params_hash not in self._async_http_clients:
            options = self._get_transport_options(override=rate_limit_options or retry_options)
            transport = AsyncRateLimitTransport(**options) if rate_limit_options else AsyncRetryTransport(**options)

            client = ReusableAsyncHttpxClient(
                **kwargs,
                **self._get_client_options(override=client_options),
                transport=transport,
                on_before_close_callback=lambda: self._async_http_clients.pop(params_hash),
            )
            self._async_http_clients[params_hash] = client

        http_client = self._async_http_clients.get(params_hash)
        assert isinstance(http_client, AsyncHttpxClient)
        assert not http_client.is_closed
        return http_client

    def _get_headers(self, override: Optional[dict]) -> dict:
        headers = {
            **(override or {}),
            "Authorization": f"Bearer {self._credentials.api_key.get_secret_value()}",
            "x-request-origin": f"python-sdk/{__version__}",
            "user-agent": f"python-sdk/{__version__}",
        }

        return headers

    def _get_client_options(self, override: Optional[dict] = None) -> dict:
        final = merge_objects(
            self.config.client_options.model_dump(exclude_none=True),
            override,
            {
                "base_url": self._credentials.api_endpoint,
                "headers": self._get_headers(override=(override or {}).get("headers")),
            },
        )
        return HttpClientOptions.model_validate(final).model_dump()

    def _get_transport_options(self, override: Optional[dict] = None) -> dict:
        return merge_objects(self.config.transport_options.model_dump(exclude_none=True), override)
