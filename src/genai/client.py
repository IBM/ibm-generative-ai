from typing import Generic, Optional, Type, TypeVar, Union, cast

from genai.credentials import Credentials
from genai.services.generate_service import GenerationService
from genai.services.model_service import ModelService
from genai.services.prompt_template_service import PromptTemplateService
from genai.services.tokenize_service import TokenizeService
from genai.services.tune_service import TuneService

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")


class ServicesContainer(Generic[A, B, C, D, E]):
    generation: Type[A]
    template: Type[B]
    model: Type[C]
    tune: Type[D]
    tokenize: Type[E]

    def __init__(
        self,
        generation: Optional[Type[A]] = None,
        template: Optional[Type[B]] = None,
        model: Optional[Type[C]] = None,
        tune: Optional[Type[D]] = None,
        tokenize: Optional[Type[E]] = None,
    ) -> None:
        self.generation = generation or GenerationService
        self.template = template or PromptTemplateService
        self.model = model or ModelService
        self.tune = tune or TuneService
        self.tokenize = tokenize or TokenizeService


class Client(Generic[A, B, C, D, E]):
    def __init__(
        self,
        credentials: Credentials,
        *,
        services: Optional[ServicesContainer[A, B, C, D, E]] = None,
    ) -> None:
        self.credentials = credentials

        if services is None:
            services = ServicesContainer[A, B, C, D, E]()

        assert issubclass(services.generation, GenerationService)
        self.generation: Union[A, GenerationService] = cast(A, services.generation(credentials=credentials))

        assert issubclass(services.template, PromptTemplateService)
        self.template: Union[B, PromptTemplateService] = cast(B, services.template(credentials=credentials))

        assert issubclass(services.model, ModelService)
        self.model: Union[C, ModelService] = cast(C, services.model(credentials=credentials))

        assert issubclass(services.tune, TuneService)
        self.tune: Union[D, TuneService] = cast(D, services.tune(credentials=credentials))

        assert issubclass(services.tokenize, TokenizeService)
        self.tokenize: Union[E, TokenizeService] = cast(E, services.tokenize(credentials=credentials))
