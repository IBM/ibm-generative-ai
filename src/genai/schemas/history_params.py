from typing import Literal, Optional

from pydantic import BaseModel, Extra, Field

from genai.schemas import Descriptions as tx

# API Reference : https://workbench.res.ibm.com/docs


class HistoryParams(BaseModel):
    class Config:
        anystr_strip_whitespace: True
        extra: Extra.forbid

    limit: Optional[int] = Field(None, description=tx.LIMIT, le=100)
    offset: Optional[int] = Field(None, description=tx.OFFSET)
    status: Optional[Literal["SUCCESS", "ERROR"]] = Field(None, description=tx.STATUS)
    origin: Optional[Literal["API", "UI"]] = Field(None, description=tx.ORIGIN)
