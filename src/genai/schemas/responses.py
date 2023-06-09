import logging
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Extra, root_validator

from genai.schemas.generate_params import GenerateParams
from genai.schemas.models import ModelType

logger = logging.getLogger(__name__)


class StopReasonEnum(str, Enum):
    NOT_FINISHED = "Possibly more tokens to be streamed"
    MAX_TOKENS = "Maximum requested tokens reached"
    EOS_TOKEN = "End of sequence token encountered"
    CANCELLED = "Request canceled by the client"
    TIME_LIMIT = "Time limit reached"
    STOP_SEQUENCE = "Stop sequence encountered"
    TOKEN_LIMIT = "Token limit reached"
    ERROR = "Error encountered"


def alert_extra_fields_validator(cls, values) -> dict:
    """Reusable validator that logs a warning if we see undocmented fields returned by the API

    Args:
        cls (ModelMetaclass): the pydantic model that is being validated
        values (dict): The incoming values to be checkec

    Returns:
        dict: The values post validation
    """
    extra_fields = values.keys() - cls.__fields__.keys()

    if extra_fields:
        logger.warning(
            f"Extra fields missing from {cls.__name__}. Add Optional[Type] typing for these fields: {extra_fields}"
        )

    return values


class GenAiResponseModel(BaseModel, extra=Extra.allow):
    # Validators
    _extra_fields_warning = root_validator(allow_reuse=True)(alert_extra_fields_validator)


class TermsOfUseResult(GenAiResponseModel):
    tou_accepted: bool
    tou_accepted_at: datetime
    firstName: str
    lastName: str
    data_usage_consent: bool = False
    generate_default: dict = None


class TermsOfUse(GenAiResponseModel):
    results: TermsOfUseResult


class GeneratedToken(GenAiResponseModel):
    logprob: Optional[float]
    text: Optional[str]


class GenerateResult(GenAiResponseModel):
    generated_text: str
    generated_token_count: int
    input_token_count: Optional[int]
    stop_reason: str
    generated_tokens: Optional[list[GeneratedToken]]
    input_text: Optional[str]
    seed: Optional[int]


class GenerateResponse(GenAiResponseModel):
    model_id: Union[ModelType, str]
    created_at: datetime
    results: List[GenerateResult]


class GenerateStreamResponse(GenAiResponseModel):
    generated_text: Optional[str]
    generated_token_count: Optional[int]
    input_token_count: Optional[int]
    stop_reason: Optional[str]
    generated_tokens: Optional[list[GeneratedToken]]
    input_text: Optional[str]
    seed: Optional[int]


class TokenizeResult(GenAiResponseModel):
    token_count: Optional[int]
    tokens: Optional[List[str]]
    input_text: Optional[str]


class TokenizeResponse(GenAiResponseModel):
    model_id: Union[ModelType, str]
    created_at: datetime
    results: List[TokenizeResult]


class HistoryResultRequest(GenAiResponseModel):
    inputs: list[str]
    model_id: str
    parameters: GenerateParams


class HistoryResult(GenAiResponseModel):
    id: str
    duration: int
    request: HistoryResultRequest
    status: str
    created_at: datetime
    response: Union[GenerateResponse, Any]


class HistoryResponse(GenAiResponseModel):
    results: List[HistoryResult]
    totalCount: int


class ErrorExtensionStateParam(GenAiResponseModel):
    comparison: str
    limit: int


class ErrorExtensionState(GenAiResponseModel):
    instancePath: str
    params: ErrorExtensionStateParam


class ErrorExtensions(GenAiResponseModel):
    code: str
    state: list[ErrorExtensionState]


class ErrorResponse(GenAiResponseModel):
    status_code: int
    error: str
    message: str
    extensions: Optional[ErrorExtensions]
