from typing import Any, Optional

import httpx
from typing_extensions import TypeGuard

from genai.schema import (
    BadRequestResponse,
    BaseErrorResponse,
    InternalServerErrorResponse,
    NotFoundResponse,
    TooManyRequestsResponse,
    UnauthorizedResponse,
)

__all__ = [
    "is_api_error_response",
    "get_api_error_class_by_status_code",
    "to_api_error",
    "BaseErrorResponse",
]


def is_api_error_response(input: Any) -> TypeGuard[BaseErrorResponse]:
    return isinstance(input, BaseErrorResponse)


def get_api_error_class_by_status_code(code: int) -> Optional[type[BaseErrorResponse]]:
    response_class_mapping: dict[int, type[BaseErrorResponse]] = {
        httpx.codes.TOO_MANY_REQUESTS.value: TooManyRequestsResponse,
        httpx.codes.NOT_FOUND.value: NotFoundResponse,
        httpx.codes.UNAUTHORIZED.value: UnauthorizedResponse,
        httpx.codes.INTERNAL_SERVER_ERROR.value: InternalServerErrorResponse,
        httpx.codes.BAD_REQUEST.value: BadRequestResponse,
    }
    return response_class_mapping.get(code)


def to_api_error(body: dict) -> BaseErrorResponse:
    cls: type[BaseErrorResponse] = get_api_error_class_by_status_code(body["status_code"]) or BaseErrorResponse
    model = cls.model_validate(body)
    return model
