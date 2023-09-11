from typing import Generator, List, Optional, Type, TypeVar, Union

from genai import Credentials, Options, PromptPattern
from genai.client import Client, Container
from genai.extensions.localserver import CustomModel
from genai.schemas import GenerateResult, TokenizeResult, TokenParams
from genai.services.generate_service import GenerateService, Params
from genai.services.tokenize_service import TokenizeService

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")


class LocalClient(Client[A, B, C, D, E]):
    def __init__(self, *, services: Optional[Container[A, B, C, D, E]] = None) -> None:
        credentials = Credentials(api_key="")
        super().__init__(credentials, services=services)

    def set_credentials(self, credentials: Credentials):
        self.credentials.api_key = credentials.api_key
        self.credentials.api_endpoint = credentials.api_endpoint

    @classmethod
    def from_models(cls, custom_models: List[Type[CustomModel]]):
        models = {model.model_id: model() for model in custom_models}

        def to_string(input: Union[str, PromptPattern]) -> str:
            if type(input) != str:
                raise Exception("Only plain strings are supported!")
            return input

        class CustomGenerateService(GenerateService):
            def generate_as_completed(
                self,
                model: str,
                params: Params,
                prompts: Union[list[str], list[PromptPattern]],
                options: Optional[Options] = None,
            ) -> Generator[GenerateResult, None, None]:
                model_instance = models[model]
                for prompt in prompts:
                    yield model_instance.generate(input_text=to_string(prompt), params=params)

        class CustomTokenizeService(TokenizeService):
            def tokenize_as_completed(
                self,
                model_id: str,
                prompts: Union[list[str], list[PromptPattern]],
                params: Optional[TokenParams] = None,
                options: Optional[Options] = None,
            ) -> Generator[TokenizeResult, None, None]:
                model_instance = models[model_id]
                for prompt in prompts:
                    yield model_instance.tokenize(input_text=to_string(prompt), params=params or TokenParams())

        return cls(services=Container(generate=CustomGenerateService, tokenize=CustomTokenizeService))
