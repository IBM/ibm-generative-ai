from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from genai.schemas import Descriptions as tx

# API Reference : https://workbench.res.ibm.com/docs


class TokenParams(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    return_tokens: Optional[bool] = Field(None, description=tx.RETURN_TOKEN)
