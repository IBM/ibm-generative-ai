import logging
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Extra, root_validator

from genai.schemas.generate_params import GenerateParams

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


class TextPosition(GenAiResponseModel):
    start: int
    end: int


class HAPResult(GenAiResponseModel):
    flagged: bool
    score: float
    success: bool
    position: TextPosition


class ModerationResult(GenAiResponseModel):
    hap: List[HAPResult]


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
    moderation: Optional[ModerationResult]


class GenerateResponse(GenAiResponseModel):
    id: str
    model_id: str
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
    moderation: Optional[ModerationResult]


class TokenizeResult(GenAiResponseModel):
    token_count: Optional[int]
    tokens: Optional[List[str]]
    input_text: Optional[str]


class TokenizeResponse(GenAiResponseModel):
    model_id: str
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


class WatsonxTemplate(GenAiResponseModel):
    id: str
    name: str
    value: str
    created_at: datetime
    data: Optional[dict]


class WatsonxTemplatesResponse(GenAiResponseModel):
    results: list[WatsonxTemplate]
    totalCount: int


class WatsonxRenderedPrompts(GenAiResponseModel):
    results: list[str]


class FileFormatResult(GenAiResponseModel):
    id: int
    name: str


class FileInfoResult(GenAiResponseModel):
    id: str
    bytes: str
    file_name: str
    purpose: str
    storage_provider_location: Optional[str]
    created_at: datetime
    file_formats: List[FileFormatResult]


class FilesListResponse(GenAiResponseModel):
    results: List[FileInfoResult]
    totalCount: int


class TuneParameters(GenAiResponseModel):
    accumulate_steps: Optional[int]
    batch_size: Optional[int]
    learning_rate: Optional[float]
    max_input_tokens: Optional[int]
    max_output_tokens: Optional[int]
    num_epochs: Optional[int]
    num_virtual_tokens: Optional[int]
    verbalizer: Optional[str]


class TuneInfoResult(GenAiResponseModel):
    id: str
    name: str
    model_id: str
    model_name: str
    method_id: Optional[str]
    method_name: Optional[str]
    status: str
    task_id: str
    task_name: Optional[str]
    parameters: Optional[TuneParameters]
    created_at: datetime
    preferred: Optional[bool]
    datapoints: Optional[dict]
    validation_files: Optional[list]
    training_files: Optional[list]
    evaluation_files: Optional[list]
    status_message: Optional[str]
    started_at: Optional[datetime]


class TunesListResponse(GenAiResponseModel):
    results: List[TuneInfoResult]
    totalCount: int


class TrainingFilesParameters(GenAiResponseModel):
    id: str
    file_name: str
    created_at: str


class TuneGetResponse(GenAiResponseModel):
    results: Optional[TuneInfoResult]


class TuneMethodsInfo(GenAiResponseModel):
    id: str
    name: str


class TuneMethodsGetResponse(GenAiResponseModel):
    results: Optional[List[TuneMethodsInfo]]


class FileFormatResult(GenAiResponseModel):
    id: int
    name: str


class FileInfoResult(GenAiResponseModel):
    id: str
    bytes: str
    file_name: str
    purpose: str
    storage_provider_location: Optional[str]
    created_at: datetime
    file_formats: List[FileFormatResult]


class TuneParameters(GenAiResponseModel):
    accumulate_steps: Optional[int]
    batch_size: Optional[int]
    learning_rate: Optional[float]
    max_input_tokens: Optional[int]
    max_output_tokens: Optional[int]
    num_epochs: Optional[int]
    num_virtual_tokens: Optional[int]
    verbalizer: Optional[str]


class TuneInfoResult(GenAiResponseModel):
    id: str
    name: str
    model_id: str
    model_name: str
    method_id: Optional[str]
    method_name: Optional[str]
    status: str
    task_id: str
    task_name: Optional[str]
    parameters: Optional[TuneParameters]
    created_at: datetime
    preferred: Optional[bool]
    datapoints: Optional[dict]
    validation_files: Optional[list]
    training_files: Optional[list]
    evaluation_files: Optional[list]
    status_message: Optional[str]
    started_at: Optional[datetime]


class ModelCard(GenAiResponseModel):
    id: Optional[str]
    name: Optional[str]
    size: Optional[str]
    source_model_id: Optional[str]
    token_limit: Optional[Union[int, Any]]


class ModelList(GenAiResponseModel):
    results: list[ModelCard]


class GenerateLimits(GenAiResponseModel):
    tokenCapacity: int
    tokensUsed: int
