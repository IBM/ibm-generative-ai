import typing
from typing import Any, Optional

import httpx
from httpx._models import Headers, Response
from httpx._types import HeaderTypes, QueryParamTypes
from httpx_sse import SSEError, connect_sse

from genai._utils.general import merge_objects
from genai._utils.responses import BaseErrorResponse
from genai.exceptions import ApiResponseException


class HttpxClient(httpx.Client):
    """
    This class represents an HTTP client based on the `httpx.Client` class with some extra methods.

    Note:
        use HttpxClient instead of httpx.Client across the project
    """

    def post_stream(
        self,
        url: str,
        *,
        headers: Optional[HeaderTypes] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
    ):
        with connect_sse(
            client=self,
            method="POST",
            url=url,
            headers=merge_objects(self.headers, Headers(headers)),
            json=json,
            params=params,
        ) as event_source:
            try:
                for sse in event_source.iter_sse():
                    if sse.event == "error":
                        if sse.data.startswith("{") and sse.data.endswith("}"):
                            raise ApiResponseException(response=BaseErrorResponse(**sse.json()))
                        else:
                            raise ValueError(f"Invalid server response during streaming!\nRetrieved data: {sse.data}")

                    yield sse.data
            except SSEError as e:
                response: Response = event_source.response
                if "application/json" in response.headers["content-type"]:
                    response.read()
                    raise ApiResponseException(  # noqa: B904
                        message="Invalid data chunk retrieved during streaming.", response=response
                    )
                raise e


class AsyncHttpxClient(httpx.AsyncClient):
    """
    This class represents an asynchronous HTTP client based on the `httpx.AsyncClient` class.

    Note: use AsyncHttpxClient instead of httpx.AsyncClient across the project
    """


class ReusableAsyncHttpxClient(AsyncHttpxClient):
    """
    This class extends the `AsyncHttpxClient` class and allows for reusing the client instance by maintaining a
    reference count. It provides the ability to close the client when the reference count reaches zero, as well as
    entering and exiting context for managing the reference count.
    """

    def __init__(self, *args, on_before_close_callback: typing.Callable, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._ref_count = 0
        self._on_before_close_callback = on_before_close_callback

    async def aclose(self) -> None:
        self._ref_count -= 1
        if self._ref_count == 0:
            self._ref_count = 0
            self._on_before_close_callback()
            await super().aclose()

    async def __aenter__(self):
        if self._ref_count > 0:
            self._ref_count += 1
            return self

        if self._ref_count == 0:
            self._ref_count = 1
            await super().__aenter__()

        return self

    async def __aexit__(self, *args):
        self._ref_count -= 1

        if self._ref_count == 0:
            self._on_before_close_callback()
            await super().__aexit__(*args)
            self._ref_count = 0
