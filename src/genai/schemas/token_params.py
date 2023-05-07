from typing import Optional

from pydantic import BaseModel, Extra, Field

from genai.schemas import Descriptions as tx

# API Reference : https://workbench.res.ibm.com/docs


class TokenParams(BaseModel):
    class Config:
        anystr_strip_whitespace: True
        extra: Extra.forbid

    return_tokens: Optional[bool] = Field(None, description=tx.RETURN_TOKEN)
