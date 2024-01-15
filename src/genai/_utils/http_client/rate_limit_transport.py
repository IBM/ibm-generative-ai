from typing import Optional

from aiolimiter import AsyncLimiter
from httpx import Request, Response

__all__ = ["AsyncRateLimiter", "AsyncRateLimitTransport"]

from genai._utils.http_client.retry_transport import AsyncRetryTransport


class AsyncRateLimiter(AsyncLimiter):
    """Modified version of AsyncLimiter with no-bursting approach and customizable limits"""

    def __init__(self, max_rate: float, time_period: float) -> None:
        super().__init__(max_rate=1, time_period=time_period / max_rate)
        self._source_max_rate = max_rate
        self._source_time_period = time_period

    def update_limit(self, *, max_rate: Optional[float] = None, time_period: Optional[float] = None) -> None:
        """Updates the maximum rate and time period for the source.

        Args:
            max_rate: The maximum rate for the source.
            time_period: The time period for the source.
        """
        if max_rate is None:
            max_rate = self._source_max_rate
        else:
            self._source_max_rate = max_rate

        if time_period is None:
            time_period = self._source_time_period
        else:
            self._source_time_period = time_period

        self.max_rate = 1
        self.time_period = time_period / max_rate
        self._rate_per_sec = self.max_rate / self.time_period


class AsyncRateLimitTransport(AsyncRetryTransport):
    """
    Transport class that enforces rate limiting for asynchronous requests.

    Args:
        *args: Variable length argument list passed to `AsyncRetryTransport`.
        max_rate: The default maximum rate allowed for requests (in requests per time_period).
        time_period: The default time period for rate limiting (in seconds).
        disable_rate_limit_no_header: disable rate limiting if the response header has no rate limit information.
        **kwargs: Keyword arguments passed to AsyncRetryTransport.
    """

    def __init__(
        self,
        *args,
        max_rate: float,
        time_period: float = 1.0,
        disable_rate_limit_no_header: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._active: bool = True
        self._disable_rate_limit_no_header = disable_rate_limit_no_header
        self._limiter = AsyncRateLimiter(max_rate=max_rate, time_period=time_period)

    def _update_rate_limit(self, response: Response):
        max_rate = response.headers.get("x-ratelimit-limit")

        if max_rate is not None:
            self._active = True
            self._limiter.update_limit(
                max_rate=max(int(max_rate), 1),
            )
        elif self._disable_rate_limit_no_header:
            self._active = False

    async def handle_async_request(
        self,
        request: Request,
    ) -> Response:
        if not self._active:
            return await super().handle_async_request(request)

        async with self._limiter:
            response = await super().handle_async_request(request)
            self._update_rate_limit(response)
            return response
