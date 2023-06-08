from genai.model import TokenParams
from genai.schemas.generate_params import GenerateParams
from genai.schemas.responses import GenAiResponseModel


class GenerateRequestBody(GenAiResponseModel):
    model_id: str
    inputs: list[str]
    parameters: GenerateParams


class TokenizeRequestBody(GenAiResponseModel):
    model_id: str
    inputs: list[str]
    parameters: TokenParams
