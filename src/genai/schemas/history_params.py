from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from genai.schemas import Descriptions as tx

# API Reference : https://workbench.res.ibm.com/docs


class HistoryParams(BaseModel):
    model_config = ConfigDict()

    limit: Optional[int] = Field(None, description=tx.LIMIT, le=100)
    offset: Optional[int] = Field(None, description=tx.OFFSET)
    status: Optional[Literal["SUCCESS", "ERROR"]] = Field(None, description=tx.STATUS)
    origin: Optional[Literal["API", "UI"]] = Field(None, description=tx.ORIGIN)
