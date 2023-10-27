from genai.credentials import Credentials
# from genai.model import GenAiException

import os, logging

from langchain.pydantic_v1 import Field, BaseModel

from genai import Credentials
from genai import Model

from typing import (
    Any,
)

logger = logging.getLogger(__name__)

__all__ = ["BAM"]


class BAM(BaseModel):
    model_name: str = Field(default="ibm/falcon-40b-8lang-instruct", alias="model")
    """Model name to use."""
    watsonx_api_key: str = None
    watsonx_api_base: str = None
    watsonx_organization: str = "ibm"
    model_kwargs: dict[str, Any] = None
    model: Any = None 

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True
    
 
    def create(self, messages: str = None, **kwargs: Any ) -> Any:
        
        logging.debug(f'\tIn BAM.create\nmessages = {messages}\n')
        prompts = []
        for m in messages:
            logging.debug(f'm.role = {m["role"]}')
            prompts.append(m["content"])

        logging.debug(f'\tIn BAM.create\messages = {messages}\n')
        logging.debug(f'\tIn BAM.create\nprompts = {prompts}\n')
        logging.debug(f'In - BAM.create - kwargs = {kwargs}')
        creds = Credentials(self.watsonx_api_key, self.watsonx_api_base)

        model = Model(self.model_name, params=self.model_kwargs, credentials=creds)

        response = {}
        res = {}
        res["message"] = {}
        response ["choices"] = []
        result = model.generate(prompts)
        for index, rsp in enumerate(result):
            
            res["message"]["content"] = rsp.generated_text
            res["message"]["role"] = messages[index]["role"]
            response ["choices"].append(res)
            
        return response

