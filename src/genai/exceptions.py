import logging
import typing
from typing import Union

from httpx import HTTPError, Response
from pydantic import ValidationError as _ValidationError
from typing_extensions import TypeAlias

from genai._utils.responses import is_api_error_response, to_api_error
from genai.schema import BaseErrorResponse

logger = logging.getLogger(__name__)

__all__ = ["BaseApiException", "ApiResponseException", "ApiNetworkException", "ValidationError"]


ValidationError: TypeAlias = _ValidationError


class BaseApiException(Exception):
    """
    Exception class for API related errors.
    """

    message: str


class ApiResponseException(BaseApiException):
    """
    Exception class for API with valid response body.
    """

    response: BaseErrorResponse

    def __init__(
        self,
        response: Union[Response, BaseErrorResponse],
        message: str = "Server Error",
        *args,
    ) -> None:
        if is_api_error_response(response):
            self.response = response
        elif isinstance(response, Response):
            self.response = to_api_error(response)
        else:
            raise TypeError(f"Expected either Response or Api Error Response, but {type(response)} received.")

        message = f"{message}\n{self.response.model_dump_json(indent=2)}"
        super().__init__(message, *args)


class ApiNetworkException(BaseApiException):
    """
    Exception raised when there is a network-related error during API communication ('httpx' related error).

    Attributes:
        message (str): Explanation of the error.
    """

    __cause__: typing.Optional[HTTPError] = None

    def __init__(self, message: typing.Optional[str] = None, *args) -> None:
        self.message = message or "Network Exception has occurred. Try again later."
        super().__init__(self.message, *args)
