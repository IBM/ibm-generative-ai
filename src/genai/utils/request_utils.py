from pydantic import BaseModel


def sanitize_params(params):
    if isinstance(params, BaseModel):
        params = params.model_dump(by_alias=True, exclude_none=True)
    return params
