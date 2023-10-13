import asyncio
from typing import List, Optional

import httpx
from aiolimiter import AsyncLimiter
from httpx import HTTPStatusError, Request, RequestError, Response

__all__ = ["AsyncRateLimiter", "AsyncRateLimitTransport", "AsyncRetryTransport"]


class AsyncRateLimiter(AsyncLimiter):
    def update_limit(self, *, max_rate: Optional[float] = None, time_period: Optional[float] = None):
        self.max_rate = max_rate or self.max_rate
        self.time_period = time_period or self.time_period
        self._rate_per_sec = self.max_rate / self.time_period


class AsyncRetryTransport(httpx.AsyncHTTPTransport):
    def __init__(self, *args, retry_status_codes: Optional[List[int]] = None, backoff_factor: float = 0.2, **kwargs):
        self.retry_status_codes = retry_status_codes or [
            httpx.codes.TOO_MANY_REQUESTS,
            httpx.codes.BAD_GATEWAY,
            httpx.codes.SERVICE_UNAVAILABLE,
        ]
        self.backoff_factor = backoff_factor
        self.retries = kwargs.get("retries", 0)
        super().__init__(*args, **kwargs)

    def _get_retry_delays(self):
        yield 0
        for i in range(self.retries):
            yield self.backoff_factor * (2**i)

    async def handle_async_request(
        self,
        request: Request,
    ) -> Response:
        latest_err: Optional[Exception] = None

        for delay in self._get_retry_delays():
            if delay > 0:
                await asyncio.sleep(delay)

            try:
                response = await super().handle_async_request(request)
                response.request = request
                response.raise_for_status()
                return response
            except HTTPStatusError as ex:
                latest_err = ex
                if ex.response.status_code in self.retry_status_codes:
                    continue
                raise ex

        raise RequestError(f"Failed to handle request to {request.url}", request=request) from latest_err


class AsyncRateLimitTransport(AsyncRetryTransport):
    def __init__(self, *args, default_max_rate: float, default_time_period: float, **kwargs):
        super().__init__(*args, **kwargs)
        self.limiter = AsyncRateLimiter(max_rate=default_max_rate, time_period=default_time_period)

    def update_rate_limit(self, response: Response):
        max_capacity = response.headers.get("x-ratelimit-limit")
        reset_period_in_seconds = response.headers.get("x-ratelimit-reset")

        if max_capacity and reset_period_in_seconds:
            self.limiter.update_limit(
                max_rate=max(1, int(max_capacity)),
                time_period=max(1, int(reset_period_in_seconds)),
            )

    async def handle_async_request(
        self,
        request: Request,
    ) -> Response:
        async with self.limiter:
            response = await super().handle_async_request(request)
            self.update_rate_limit(response)
            return response
