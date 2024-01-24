import asyncio
import time
from abc import ABC
from enum import Enum
from typing import Optional, Sequence, Union

from httpx import (
    AsyncHTTPTransport,
    HTTPError,
    HTTPStatusError,
    HTTPTransport,
    Request,
    RequestError,
    Response,
    codes,
)

from genai.exceptions import ApiResponseException

__all__ = ["RetryTransport", "AsyncRetryTransport"]

from genai.exceptions import ApiNetworkException


class BaseRetryTransport(ABC):
    """
    BaseRetryTransport is an abstract base class that provides the basic functionality
    for a retry transport in an API client.

    Attributes:
        Callback: An enumeration of callback types for retry handling.

            - Success: Indicates a successful request.
            - Retry: Indicates a retry attempt.
            - ThresholdReached: Indicates that the retry threshold has been reached.

        default_retry_status_codes (list[int]): The default list of HTTP status codes that should trigger a retry.

    Notes:
        Automatically validates response HTTP status codes.

    """

    class Callback(str, Enum):
        Success = "success"
        Retry = "on_retry"
        ThresholdReached = "on_threshold_reached"

    default_retry_status_codes = [
        codes.TOO_MANY_REQUESTS,
        codes.BAD_GATEWAY,
        codes.SERVICE_UNAVAILABLE,
        codes.CONFLICT,
        codes.TOO_EARLY,
        codes.GATEWAY_TIMEOUT,
        codes.REQUEST_TIMEOUT,
        codes.INTERNAL_SERVER_ERROR,
    ]

    def __init__(
        self,
        *args,
        retry_status_codes: Optional[Sequence[int]] = None,
        backoff_factor: float = 0.2,
        **kwargs,
    ):
        """
        Raises:
            ValueError: If retry_status_codes is provided but is not a list.
        """
        if retry_status_codes is not None and not isinstance(retry_status_codes, list):
            raise ValueError('The "retry_status_code" parameter should be list of status codes!')

        self._retry_status_codes: list[int] = (
            self.default_retry_status_codes if retry_status_codes is None else retry_status_codes
        )
        self._backoff_factor = backoff_factor
        self.retries = kwargs.get("retries", 3)
        super().__init__(*args, **kwargs)

    def _get_execution_plan(self):
        yield 0
        for idx in range(self.retries):
            yield self._backoff_factor * (2**idx)

    def _is_json_response(self, response: Optional[Response]) -> bool:
        return response is not None and "application/json" in response.headers.get("Content-Type", "")

    def _create_exception(
        self, *, exception: Exception, request: Request, requests_count: int
    ) -> Union[ApiResponseException, ApiNetworkException]:
        if isinstance(exception, HTTPStatusError):
            message = (
                f"Failed to handle request after {requests_count - 1} retries to {request.url}."
                if requests_count > 1
                else f"Failed to handle request to {request.url}."
            )

            return ApiResponseException(
                message=message,
                response=exception.response,
            )
        else:
            return ApiNetworkException(f"Network error has occurred (target {request.url}).")


class RetryTransport(BaseRetryTransport, HTTPTransport):
    """
    RetryTransport class handles retrying of HTTP requests with configurable delays and error handling.
    """

    def handle_request(
        self,
        request: Request,
    ) -> Response:
        """
        Raises:
            HTTPStatusError: If the response status code is not in the retry status codes.
            HTTPError: If an HTTP error occurs.
        """
        latest_err: Optional[HTTPError] = None
        requests_count: int = 0

        for delay in self._get_execution_plan():
            requests_count += 1
            if delay > 0:
                time.sleep(delay)

            try:
                response = super().handle_request(request)
                response.request = request
                response.raise_for_status()
                self._execute_callback(self.Callback.Success, request=request, callback_args=[response])
                return response
            except HTTPStatusError as e:
                latest_err = e
                e.response.read()

                if e.response.status_code not in self._retry_status_codes:
                    break

                self._execute_callback(self.Callback.Retry, request=request, callback_args=[e])
            except HTTPError as e:
                latest_err = e
                self._execute_callback(self.Callback.Retry, request=request, callback_args=[e])

        self._execute_callback(self.Callback.ThresholdReached, request=request, callback_args=[])
        raise self._create_exception(
            exception=latest_err, request=request, requests_count=requests_count
        ) from latest_err

    def _execute_callback(self, name: BaseRetryTransport.Callback, request: Request, callback_args: list):
        callback = request.extensions.get(name)
        if callback:
            callback(*callback_args)


class AsyncRetryTransport(BaseRetryTransport, AsyncHTTPTransport):
    """
    Transport responsible for handling asynchronous requests with built-in retry logic.
    """

    async def handle_async_request(
        self,
        request: Request,
    ) -> Response:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        latest_err: Optional[HTTPError] = None
        requests_count: int = 0

        for delay in self._get_execution_plan():
            requests_count += 1
            if delay > 0:
                await asyncio.sleep(delay)

            try:
                response = await super().handle_async_request(request)
                response.request = request
                response.raise_for_status()
                await self._execute_async_callback(self.Callback.Success, request=request, callback_args=[response])
                return response
            except HTTPStatusError as e:
                latest_err = e
                await e.response.aread()

                if e.response.status_code not in self._retry_status_codes:
                    break

                await self._execute_async_callback(self.Callback.Retry, request=request, callback_args=[e])
            except RequestError as e:
                latest_err = e
                await self._execute_async_callback(self.Callback.Retry, request=request, callback_args=[e])

        await self._execute_async_callback(self.Callback.ThresholdReached, request=request, callback_args=[])
        raise self._create_exception(
            exception=latest_err, request=request, requests_count=requests_count
        ) from latest_err

    async def _execute_async_callback(self, name: BaseRetryTransport.Callback, request: Request, callback_args: list):
        callback = request.extensions.get(name)
        if callback:
            await callback(*callback_args)
