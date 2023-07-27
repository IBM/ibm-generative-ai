from typing import Optional

from pydantic import BaseModel, Extra, Field

from genai.schemas.descriptions import FilesAPIDescriptions as tx


class FileListParams(BaseModel):
    """Class to hold the parameters for file listing."""

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    limit: Optional[int] = Field(None, description=tx.LIMIT, le=100)
    offset: Optional[int] = Field(None, description=tx.OFFSET)
    search: Optional[str] = Field(None, description=tx.SEARCH)


class MultipartFormData(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    purpose: str = Field(..., description=tx.PURPOSE)
    file: str = Field(..., description=tx.FILE)
