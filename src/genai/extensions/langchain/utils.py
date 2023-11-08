from typing import Any, Optional, Union

from langchain.schema import LLMResult
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

    return {
        "prompt_tokens": get_count_value("input_token_count"),
        "completion_tokens": get_count_value("generated_token_count"),
        "total_tokens": get_count_value("input_token_count") + get_count_value("generated_token_count"),
        # For backward compatibility
        "generated_token_count": get_count_value("generated_token_count"),
        "input_token_count": get_count_value("input_token_count"),
    }


def update_token_usage(*, target: dict[str, Any], sources: list[Optional[dict[str, Any]]]):
    for source in sources:
        if not source:
            continue

        for key, value in extract_token_usage(source).items():
            if key in target:
                target[key] += value
            else:
                target[key] = value


def update_llm_result(current: LLMResult, generation_info: dict[str, Any]):
    if current.llm_output is None:
        current.llm_output = {}

    if not current.llm_output["token_usage"]:
        current.llm_output["token_usage"] = {}

    token_usage = current.llm_output["token_usage"]
    update_token_usage(target=token_usage, sources=[generation_info])


def create_generation_info_from_response(
    response: Union[GenerateResponse, GenerateStreamResponse, ChatResponse, ChatStreamResponse]
) -> dict[str, Any]:
    result = response.results[0]
    return {"meta": response.model_dump(exclude={"results", "model_id"}), **create_generation_info_from_result(result)}


def create_generation_info_from_result(source: Union[BaseModel, dict]) -> dict:
    iterator = source if isinstance(source, BaseModel) else source.items()
    return {k: v for k, v in iterator if k not in {"generated_text"} and v is not None}


def create_llm_output(*, model: str, token_usage: Optional[dict] = None, **kwargs) -> dict[str, Any]:
    final_token_usage = extract_token_usage({})
    update_token_usage(target=final_token_usage, sources=[token_usage])
    return {"model_name": model, "token_usage": final_token_usage, **kwargs}
