import logging
from typing import Optional, Union

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
        response: Union[BaseErrorResponse, dict],
        message: Optional[str] = None,
        *args,
    ) -> None:
        if is_api_error_response(response):
            self.response = response
        elif isinstance(response, dict):
            self.response = to_api_error(response)
        else:
            raise TypeError(f"Expected either Response or Api Error Response, but {type(response)} received.")

        self.message = f"{message or 'Server Error'}\n{self.response.model_dump_json(indent=2)}"
        super().__init__(self.message, *args)

    @classmethod
    def from_http_response(cls, response: Response, message: Optional[str] = None):
        if response.is_success:
            raise ValueError("Cannot convert succeed HTTP response to error response.")

        response_body = to_api_error(response.json())
        return cls(message=message, response=response_body)

    def __reduce__(self):
        return self.__class__, (self.response.model_dump(), self.message)


class ApiNetworkException(BaseApiException):
    """
    Exception raised when there is a network-related error during API communication ('httpx' related error).

    Attributes:
        message (str): Explanation of the error.
    """

    __cause__: Optional[HTTPError] = None

    def __init__(self, message: Optional[str] = None, *args) -> None:
        self.message = message or "Network Exception has occurred. Try again later."
        super().__init__(self.message, *args)
