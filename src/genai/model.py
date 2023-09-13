import json
import logging
from builtins import bool
from collections.abc import Generator
from typing import Any, Callable, Optional, Union

from deprecated.classic import deprecated

from genai.client import Client
from genai.credentials import Credentials
from genai.options import Options
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams, TokenParams
from genai.schemas.responses import (
    GenerateResult,
    GenerateStreamResponse,
    ModelCard,
    TokenizeResult,
)
from genai.schemas.tunes_params import CreateTuneHyperParams
from genai.services import ServiceInterface
from genai.services.model_service import ModelService

logger = logging.getLogger(__name__)


@deprecated(reason="The 'Model' class is deprecated, use 'Client' class instead")
class Model:
    _accessors = set()
    _client: Client

    def __init__(
        self,
        model: str,
        params: Union[GenerateParams, TokenParams, Any] = None,
        credentials: Credentials = None,
    ):
        """Instantiates the Model Interface

        Args:
            model (str): The type of model to use
            params (Union[GenerateParams, TokenParams]): Parameters to use during generate requests
            credentials (Credentials): The API Credentials
        """
        logger.debug(
            f"Model Created:  Model: {model}, endpoint: {credentials.api_endpoint}"
        )
        self.model = model
        self.params = params
        self.creds = credentials
        self.service = ServiceInterface(
            service_url=credentials.api_endpoint, api_key=credentials.api_key
        )
        self._client = Client(credentials=credentials)

    @deprecated(reason="use client.generation.generate_stream method")
    def generate_stream(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        options: Optional[Options] = None,
    ) -> Generator[GenerateStreamResponse, None, None]:
        return self._client.generation.generate_stream(
            model=self.model, params=self.params, prompts=prompts, options=options
        )

    @deprecated(reason="use 'client.generation.generate_as_completed' method")
    def generate_as_completed(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        options: Optional[Options] = None,
    ) -> Generator[GenerateResult, None, None]:
        return self._client.generation.generate_as_completed(
            model=self.model, params=self.params, prompts=prompts, options=options
        )

    @deprecated(reason="use 'client.generation.generate' method")
    def generate(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        options: Optional[Options] = None,
    ) -> list[GenerateResult]:
        return self._client.generation.generation(
            model=self.model, params=self.params, prompts=prompts, options=options
        )

    @deprecated(reason="use 'client.generation.generate_async' method")
    def generate_async(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        ordered: bool = False,
        callback: Optional[Callable[[GenerateResult], Any]] = None,
        hide_progressbar: bool = False,
        options: Options = None,
        *,
        throw_on_error: bool = False,
    ) -> Generator[Union[GenerateResult, None], None, None]:
        return self._client.generation.generate_async(
            model=self.model,
            prompts=prompts,
            ordered=ordered,
            callback=callback,
            hide_progressbar=hide_progressbar,
            options=options,
            params=self.params,
            throw_on_error=throw_on_error,
        )

    @deprecated(reason="use 'client.tokenize.tokenize_as_completed' method")
    def tokenize_as_completed(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        options: Options = None,
        params: Optional[TokenParams] = None,
        options: Optional[Options] = None,
    ) -> Generator[TokenizeResult, None, None]:
        return self._client.tokenize.tokenize_as_completed(
            model_id=self.model,
            prompts=prompts,
            params=params,
            options=options,
        )

    @deprecated(reason="use 'client.tokenize.tokenize' method")
    def tokenize(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        return_tokens: bool = False,
        options: Optional[Options] = None,
    ) -> list[TokenizeResult]:
        return list(self.tokenize_as_completed(prompts, return_tokens, options=options))

    @deprecated(reason="use 'client.tokenize.tokenize_async' method")
    def tokenize_async(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        ordered: bool = False,
        callback: Optional[Callable[[TokenizeResult], Any]] = None,
        return_tokens: bool = False,
        options: Optional[Options] = None,
    ) -> Generator[Union[TokenizeResult, None], None, None]:
        return self._client.tokenize.tokenize_async(
            model_id=self.model,
            prompts=prompts,
            ordered=ordered,
            callback=callback,
            return_tokens=return_tokens,
            options=options,
        )

    @deprecated(reason="use 'client.tune.create' method")
    def tune(
        self,
        name: str,
        method: str,
        task: str,
        hyperparameters: CreateTuneHyperParams = None,
        training_file_ids: Optional[list[str]] = None,
        validation_file_ids: Optional[list[str]] = None,
    ):
        tuned_model = self._client.tune.create(
            source_model_id=self.model,
            name=name,
            method=method,
            task=task,
            hyperparameters=hyperparameters,
            training_file_ids=training_file_ids,
            validation_file_ids=validation_file_ids,
        )
        return Model(model=tuned_model.id, params=None, credentials=self.creds)

    @deprecated(reason="use 'client.tune.status' method")
    def status(self):
        return self._client.tune.status(tune_id=self.model)

    @deprecated(reason="use 'client.tune.delete' method")
    def delete(self):
        return self._client.tune.delete(tune_id=self.model)

    @deprecated(reason="use 'client.tune.download' method")
    def download(self, output_path: Optional[str] = None):
        return self._client.tune.download(tune_id=self.model, output_path=output_path)

    @staticmethod
    @deprecated(reason="use 'client.model.list' method")
    def models(
        credentials: Credentials = None, service: ServiceInterface = None
    ) -> list[ModelCard]:
        return ModelService(credentials=credentials, service=service).list()

    @deprecated(reason="use 'client.model.available' method")
    def available(self) -> bool:
        return self._client.model.available(model_id=self.model)

    def info(self) -> Union[ModelCard, None]:
        return self._client.model.detail(model_id=self.model)

    def _get_params(self):
        if self.params is None:
            return GenerateParams()

        if isinstance(self.params, dict):
            return GenerateParams(**self.params)
        return self.params.copy()
