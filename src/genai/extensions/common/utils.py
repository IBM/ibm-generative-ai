from typing import Any, Optional, Union

from pydantic import BaseModel

from genai.schemas.responses import (
    ChatResponse,
    ChatStreamResponse,
    GenerateResponse,
    GenerateStreamResponse,
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
        # For backward compatibility
        "generated_token_count": generated_token_count,
        "input_token_count": input_token_count,
    }


def create_generation_info_from_response(
    response: Union[GenerateResponse, GenerateStreamResponse, ChatResponse, ChatStreamResponse],
    *,
    result: BaseModel,
) -> dict[str, Any]:
    result_meta = result.model_dump(exclude={"generated_text"}, exclude_none=True)

    return create_generation_info(
        meta=response.model_dump(exclude={"results", "model_id", "moderation"}, exclude_none=True),
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
