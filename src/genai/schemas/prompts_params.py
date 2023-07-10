from typing import Optional

from pydantic import BaseModel, Extra, Field

from genai.schemas import Descriptions as tx


class PromptListParams(BaseModel):
    class Config:
        anystr_strip_whitespace: True
        extra: Extra.forbid

    limit: Optional[int] = Field(None, description=tx.LIMIT, le=100)
    offset: Optional[int] = Field(None, description=tx.OFFSET)


class DataForPromptTemplate(BaseModel):
    class Config:
        anystr_strip_whitespace: True
        extra: Extra.forbid

    example_file_ids: Optional[list[str]] = Field(..., description="tx.FILE_IDS")


class PromptTemplateParams(BaseModel):
    class Config:
        anystr_strip_whitespace: True
        extra: Extra.forbid

    id: Optional[str] = Field(None, description="tx.ID")
    value: Optional[str] = Field(None, description="tx.VALUE")
    data: DataForPromptTemplate = Field(..., description="tx.DATA")
