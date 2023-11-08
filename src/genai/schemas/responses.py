import logging
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Type, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

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


def alert_extra_fields_validator(cls: Type[BaseModel], values) -> dict:
    """Reusable validator that logs a warning if we see undocmented fields returned by the API

    Args:
        cls (ModelMetaclass): the pydantic model that is being validated
        values (dict): The incoming values to be checkec

    Returns:
        dict: The values post validation
    """
    extra_fields = values.keys() - cls.model_fields.keys()

    if extra_fields:
        logger.debug(
            f"Extra fields missing from {cls.__name__}. Add Optional[Type] typing for these fields: {extra_fields}"
        )

    return values


class GenAiResponseModel(BaseModel, extra="allow"):
    # Validators
    _extra_fields_warning = model_validator(mode="before")(alert_extra_fields_validator)
    # We're protecting model_id and model_name as they are commonly used fields in BAM
    model_config = ConfigDict(protected_namespaces=())


class TermsOfUseResult(GenAiResponseModel):
    tou_accepted: bool
    tou_accepted_at: datetime
    firstName: str
    lastName: str
    data_usage_consent: bool = False
    generate_default: Optional[dict] = None


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
    logprob: Optional[float] = None
    text: Optional[str] = None


class GenerateResult(GenAiResponseModel):
    generated_text: str
    generated_token_count: int
    input_token_count: Optional[int] = None
    stop_reason: str
    stop_sequence: Optional[str] = None
    generated_tokens: Optional[list[GeneratedToken]] = None
    input_tokens: Optional[list[GeneratedToken]] = None
    input_text: Optional[str] = None
    seed: Optional[int] = None
    moderation: Optional[ModerationResult] = None


class GenerateStreamResult(GenAiResponseModel):
    generated_text: Optional[str] = None
    generated_token_count: Optional[int] = None
    input_token_count: Optional[int] = None
    stop_reason: Optional[str] = None
    generated_tokens: Optional[list[GeneratedToken]] = None
    input_tokens: Optional[list[GeneratedToken]] = None
    input_text: Optional[str] = None
    seed: Optional[int] = None
    moderation: Optional[ModerationResult] = None


class GenerateResponse(GenAiResponseModel):
    id: str
    model_id: str
    created_at: str
    results: List[GenerateResult]


class GenerateStreamResponse(GenAiResponseModel):
    id: str
    model_id: str
    created_at: str
    results: List[GenerateStreamResult] = Field(default=[])


class TokenizeResult(GenAiResponseModel):
    token_count: Optional[int] = None
    tokens: Optional[List[str]] = None
    input_text: Optional[str] = None


class TokenizeResponse(GenAiResponseModel):
    model_id: str
    created_at: str
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
    extensions: Optional[ErrorExtensions] = None


class WatsonxTemplate(GenAiResponseModel):
    id: str
    name: str
    value: str
    created_at: datetime
    data: Optional[dict] = None


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
    bytes: int
    file_name: str
    purpose: str
    storage_provider_location: Optional[str] = None
    created_at: datetime
    file_formats: List[FileFormatResult]


class FilesListResponse(GenAiResponseModel):
    results: List[FileInfoResult]
    totalCount: int


class TuneParameters(GenAiResponseModel):
    accumulate_steps: Optional[int] = None
    batch_size: Optional[int] = None
    learning_rate: Optional[float] = None
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    num_epochs: Optional[int] = None
    num_virtual_tokens: Optional[int] = None
    verbalizer: Optional[str] = None


class TuneInfoResult(GenAiResponseModel):
    id: str
    name: str
    model_id: str
    model_name: str
    method_id: Optional[str] = None
    method_name: Optional[str] = None
    status: str
    task_id: str
    task_name: Optional[str] = None
    parameters: Optional[TuneParameters] = None
    created_at: datetime
    preferred: Optional[bool] = None
    datapoints: Optional[dict] = None
    validation_files: Optional[list] = None
    training_files: Optional[list] = None
    evaluation_files: Optional[list] = None
    status_message: Optional[str] = None
    started_at: Optional[datetime] = None


class TunesListResponse(GenAiResponseModel):
    results: List[TuneInfoResult]
    totalCount: int


class TrainingFilesParameters(GenAiResponseModel):
    id: str
    file_name: str
    created_at: str


class TuneGetResponse(GenAiResponseModel):
    results: Optional[TuneInfoResult] = None


class TuneMethodsInfo(GenAiResponseModel):
    id: str
    name: str


class TuneMethodsGetResponse(GenAiResponseModel):
    results: Optional[List[TuneMethodsInfo]] = None


class ModelCard(GenAiResponseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    size: Optional[str] = None
    source_model_id: Optional[str] = None
    token_limit: Optional[Union[int, Any]] = None


class ModelList(GenAiResponseModel):
    results: list[ModelCard]


class GenerateLimits(GenAiResponseModel):
    tokenCapacity: int
    tokensUsed: int


class ChatResponse(GenerateResponse):
    conversation_id: str


class ChatStreamResponse(GenerateStreamResponse):
    conversation_id: str
    moderation: Optional[ModerationResult] = None
