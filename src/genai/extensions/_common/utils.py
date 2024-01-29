from typing import Any, Optional, Union

from genai._types import ApiBaseModel
from genai._utils.general import to_model_instance
from genai.schema import (
    TextChatCreateResponse,
    TextChatStreamCreateResponse,
    TextGenerationCreateResponse,
    TextGenerationParameters,
    TextGenerationStreamCreateResponse,
)


def extract_token_usage(result: dict[str, Any]):
    def get_count_value(key: str) -> int:
        return result.get(key, 0) or 0

    input_token_count = get_count_value("input_token_count")
    generated_token_count = get_count_value("generated_token_count")

    return {
        "prompt_tokens": input_token_count,
        "completion_tokens": generated_token_count,
        "total_tokens": input_token_count + generated_token_count,
    }


def create_generation_info_from_response(
    response: Union[
        TextGenerationCreateResponse,
        TextGenerationStreamCreateResponse,
        TextChatCreateResponse,
        TextChatStreamCreateResponse,
    ],
    *,
    result: ApiBaseModel,
) -> dict[str, Any]:
    result_meta = result.model_dump(exclude={"generated_text"}, exclude_none=True)

    return create_generation_info(
        meta=response.model_dump(exclude={"results", "moderation"}, exclude_none=True),
        token_usage=extract_token_usage(result_meta),
        **result_meta,
    )


def create_generation_info(
    *, meta: Optional[dict] = None, token_usage: Optional[dict] = None, **kwargs
) -> dict[str, Any]:
    return {
        "meta": meta or {},
        "token_usage": token_usage or extract_token_usage({}),
        **kwargs,
    }


def _prepare_generation_request(
    parameters: Optional[TextGenerationParameters] = None, *, stop: Optional[list[str]] = None, **kwargs: Any
):
    parameters = to_model_instance(parameters, TextGenerationParameters, copy=False)
    if stop is not None:
        parameters.stop_sequences = stop

    request = kwargs.copy()
    request["parameters"] = parameters

    if request.get("prompt_id") is not None:
        request.pop("input", None)
    elif request.get("input") is not None:
        request.pop("prompt_id", None)

    return request


def _prepare_chat_generation_request(**kwargs: Any):
    request = _prepare_generation_request(**kwargs)

    if request.get("conversation_id") is not None:
        request.pop("model_id", None)
        request.pop("prompt_id", None)

    if request.get("prompt_id") is not None:
        request.pop("model_id", None)

    if request.get("use_conversation_parameters") is True:
        request.pop("parameters", None)

    if request.get("parameters") is not None:
        request.pop("use_conversation_parameters", None)

    return request
