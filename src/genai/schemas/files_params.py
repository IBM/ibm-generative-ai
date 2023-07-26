from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from genai.schemas.descriptions import FilesAPIDescriptions as tx


class FileListParams(BaseModel):
    """Class to hold the parameters for file listing."""

    model_config = ConfigDict()

    limit: Optional[int] = Field(None, description=tx.LIMIT, le=100)
    offset: Optional[int] = Field(None, description=tx.OFFSET)
    search: Optional[str] = Field(None, description=tx.SEARCH)


class MultipartFormData(BaseModel):
    model_config = ConfigDict()

    purpose: str = Field(..., description=tx.PURPOSE)
    file: str = Field(..., description=tx.FILE)
