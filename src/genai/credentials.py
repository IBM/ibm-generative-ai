import re
from typing import Optional
from warnings import warn

from pydantic import BaseModel, Field, field_validator


class Credentials(BaseModel):
    api_key: str = Field(..., description="The GENAI API Key")
    api_endpoint: str = Field(..., description="GENAI API Endpoint")

    def __init__(self, api_key: str, api_endpoint: Optional[str] = "https://workbench-api.res.ibm.com", **kwargs):
        if api_key is None:
            raise ValueError("api_key must be provided")
        if api_endpoint is None:
            raise ValueError("api_endpoint must be provided")
        super().__init__(api_key=api_key, api_endpoint=api_endpoint, **kwargs)

    @field_validator("api_endpoint", mode="after")
    def format_api_endpoint(cls, value: str):
        [api, *version] = re.split(r"(/v\d+$)", value.rstrip("/"), maxsplit=1)
        if version:
            warn(
                f"The 'api_endpoint' property should not contain any explicit API version"
                f"(rename it from '{value}' to just '{api}')",
                DeprecationWarning,
            )
        return api
