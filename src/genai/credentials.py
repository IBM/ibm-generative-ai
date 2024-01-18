import os
import re
from typing import Optional

from pydantic import BaseModel, Field, SecretStr, field_validator


class Credentials(BaseModel):
    """
    The `Credentials` class represents credentials required for accessing the GENAI API.

    Attributes:
        - `api_key`: API key which can be retrieved from the UI.
        - `api_endpoint` (optional): A string representing the GENAI API endpoint (default is BAM).

    Examples:
        Create a Credentials instance with explicit api_endpoint::

            credentials = Credentials(api_key="your_api_key", api_endpoint="https://bam-api.res.ibm")

        Create a Credentials instance with default api_endpoint::

            credentials = Credentials(api_key="your_api_key")

        Create a Credentials instance from environment variables::

            credentials = Credentials.from_env()
    """

    api_key: SecretStr = Field(..., description="The GENAI API Key")
    api_endpoint: str = Field(..., description="GENAI API Endpoint", min_length=1)

    def __init__(self, api_key: str, api_endpoint: Optional[str] = None, **kwargs):
        api_endpoint = api_endpoint or "https://bam-api.res.ibm.com"

        if api_key is None:
            raise ValueError("api_key must be provided")

        super().__init__(api_key=api_key, api_endpoint=api_endpoint, **kwargs)

    @field_validator("api_endpoint", mode="after")
    def _validate_api_endpoint(cls, value: str):
        [api, *version] = re.split(r"(/v\d+$)", value.rstrip("/"), maxsplit=1)
        if version:
            raise ValueError(
                f"The 'api_endpoint' property should not contain any explicit API version"
                f"(rename it from '{value}' to just '{api}')"
            )
        return api

    @classmethod
    def from_env(cls, *, api_key_name: Optional[str] = None, api_endpoint_name: Optional[str] = None) -> "Credentials":
        return cls(
            api_key=os.environ[api_key_name or "GENAI_KEY"],
            api_endpoint=os.environ.get(api_endpoint_name or "GENAI_API", None),
        )
