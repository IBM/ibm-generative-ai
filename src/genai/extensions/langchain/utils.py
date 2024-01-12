from pathlib import Path
from typing import Any, Mapping, Optional, Union

from pydantic import BaseModel

from genai.extensions._common.utils import extract_token_usage
from genai.text.generation.schema import TextGenerationParameters


def update_token_usage(*, target: dict[str, Any], source: Optional[dict[str, Any]]):
    if not source:
        return

    for key, value in source.items():
        if key in target:
            target[key] += value
        else:
            target[key] = value


def update_token_usage_stream(*, target: dict[str, Any], source: Optional[dict]):
    if not source:
        return

    def get_value(key: str, override=False) -> int:
        current = target.get(key, 0) or 0
        new = source.get(key, 0) or 0

        if new != 0 and (current == 0 or override):
            return new
        else:
            return current

    completion_tokens = get_value("completion_tokens", override=True)
    prompt_tokens = get_value("prompt_tokens")
    target.update(
        {
            "prompt_tokens": prompt_tokens,
            "input_token_count": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": completion_tokens + prompt_tokens,
            "generated_token_count": completion_tokens,
        }
    )


def create_llm_output(*, model: str, token_usages: Optional[list[Optional[dict]]] = None, **kwargs) -> dict[str, Any]:
    final_token_usage = extract_token_usage({})
    for source in token_usages or []:
        update_token_usage(target=final_token_usage, source=source)
    return {"model_name": model, "token_usage": final_token_usage, **kwargs}


def load_config(file: Union[str, Path]) -> dict:
    def parse_config() -> dict:
        file_path = Path(file) if isinstance(file, str) else file
        if file_path.suffix == ".json":
            with open(file_path) as f:
                import json

                return json.load(f)
        elif file_path.suffix == ".yaml":
            with open(file_path, "r") as f:
                import yaml

                return yaml.safe_load(f)
        else:
            raise ValueError("File type must be json or yaml")

    config = parse_config()
    config["parameters"] = TextGenerationParameters(**config.get("parameters", {}))
    return config


def dump_optional_model(model: Optional[BaseModel]) -> Optional[Mapping[str, Any]]:
    return model.model_dump(exclude_none=True) if model else None
