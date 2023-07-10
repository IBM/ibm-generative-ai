import ast
import logging
from collections.abc import Generator
from typing import Any, Callable, Union

from tqdm import tqdm

from genai.credentials import Credentials
from genai.exceptions import GenAiException
from genai.metadata import Metadata
from genai.options import Options
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams, ModelType, TokenParams
from genai.schemas.responses import (
    GenerateResponse,
    GenerateResult,
    GenerateStreamResponse,
    TokenizeResponse,
    TokenizeResult,
)
from genai.schemas.tunes_params import (
    CreateTuneHyperParams,
    CreateTuneParams,
    TunesListParams,
)
from genai.services import AsyncResponseGenerator, ServiceInterface
from genai.services.tune_manager import TuneManager

logger = logging.getLogger(__name__)


class Model:
    _accessors = set()

    def __init__(
        self,
        model: Union[ModelType, str],
        params: Union[GenerateParams, TokenParams, Any] = None,
        credentials: Credentials = None,
    ):
        """Instantiates the Model Interface

        Args:
            model (Union[ModelType, str]): The type of model to use
            params (Union[GenerateParams, TokenParams]): Parameters to use during generate requests
            credentials (Credentials): The API Credentials
        """
        logger.debug(f"Model Created:  Model: {model}, endpoint: {credentials.api_endpoint}")
        self.model = model
        self.params = params
        self.creds = credentials
        self.service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

    def generate_stream(
        self, prompts: Union[list[str], list[PromptPattern]], options: Options = None
    ) -> Generator[GenerateStreamResponse]:
        if len(prompts) > 0 and isinstance(prompts[0], PromptPattern):
            prompts = PromptPattern.list_str(prompts)

        try:
            for i in range(0, len(prompts), Metadata.DEFAULT_MAX_PROMPTS):
                batch = prompts[i : min(i + Metadata.DEFAULT_MAX_PROMPTS, len(prompts))]

                self.params.stream = True
                response_gen = self.service.generate(self.model, batch, self.params, options=options, streaming=True)

                for chunk in response_gen:
                    if "status_code" in chunk:
                        error = ast.literal_eval(chunk)
                        raise GenAiException(error)

                    # we assume the returned string from the service is of shape "data: {...}"
                    response = chunk.replace("data:", "").strip()
                    try:
                        parsed_response = ast.literal_eval(response)
                        for result in parsed_response["results"]:
                            yield GenerateStreamResponse(**result)
                    except Exception:
                        logger.error("Could not parse {} as literal_eval".format(response))

        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)

    def generate_as_completed(
        self, prompts: Union[list[str], list[PromptPattern]], options: Options = None
    ) -> Generator[GenerateResponse]:
        """The generate endpoint is the centerpiece of the GENAI alpha.
        It provides a simplified and flexible, yet powerful interface to the supported
        models as a service. Given a text prompt as inputs, and required parameters
        the selected model (model_id) will generate a completion text as generated_text.

        Args:
            prompts (list[str]): The list of one or more prompt strings.
            options (Options, optional): Additional parameters to pass in the query payload. Defaults to None.

        Yields:
            Generator[GenerateResult]: A generator of results
        """
        if len(prompts) > 0 and isinstance(prompts[0], PromptPattern):
            prompts = PromptPattern.list_str(prompts)

        logger.debug(f"Calling Generate. Prompts: {prompts}, params: {self.params}")

        try:
            for i in range(0, len(prompts), Metadata.DEFAULT_MAX_PROMPTS):
                response_gen = self.service.generate(
                    model=self.model,
                    inputs=prompts[i : min(i + Metadata.DEFAULT_MAX_PROMPTS, len(prompts))],
                    params=self.params,
                    options=options,
                )
                if response_gen.status_code == 200:
                    response_gen = response_gen.json()
                    for y, result in enumerate(response_gen["results"]):
                        result["input_text"] = prompts[i + y]
                    responses = GenerateResponse(**response_gen)
                    for result in responses.results:
                        yield result
                else:
                    raise GenAiException(response_gen)
        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)

    def generate(
        self, prompts: Union[list[str], list[PromptPattern]], options: Options = None
    ) -> list[GenerateResponse]:
        """The generate endpoint is the centerpiece of the GENAI alpha.
        It provides a simplified and flexible, yet powerful interface to the supported
        models as a service. Given a text prompt as inputs, and required parameters
        the selected model (model_id) will generate a completion text as generated_text.

        Args:
            prompts (list[str]): The list of one or more prompt strings.
            options (Options, optional): Additional parameters to pass in the query payload. Defaults to None.

        Returns:
            list[GenerateResult]: A list of results
        """
        return list(self.generate_as_completed(prompts, options))

    def generate_async(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        ordered: bool = False,
        callback: Callable[[GenerateResult], Any] = None,
        hide_progressbar: bool = False,
        options: Options = None,
    ) -> Generator[Union[GenerateResult, None]]:
        """The generate endpoint is the centerpiece of the GENAI alpha.
        It provides a simplified and flexible, yet powerful interface to the supported
        models as a service. Given a text prompt as inputs, and required parameters
        the selected model (model_id) will generate a completion text as generated_text.
        This python method generates responses utilizing async capabilities and returns
        responses as they arrive.

        Args:
            prompts (list[str]): The list of one or more prompt strings.
            ordered (bool): Whether the responses should be returned in-order.
            callback (Callable[[GenerateResult], Any]): Optional callback
                to be called after generating result for a prompt.
            hide_progressbar (bool, optional): boolean flag to hide or show a progress bar.
                By defaul bar will be always shown.
            options (Options, optional): Additional parameters to pass in the query payload. Defaults to None.

        Returns:
            Generator[Union[GenerateResult, None]]: A list of results
        """
        if len(prompts) > 0 and isinstance(prompts[0], PromptPattern):
            prompts = PromptPattern.list_str(prompts)

        logger.debug(f"Calling Generate Async. Prompts: {prompts}, params: {self.params}")

        try:
            with AsyncResponseGenerator(
                self.model,
                prompts,
                self.params,
                self.service,
                ordered=ordered,
                callback=callback,
                options=options,
            ) as asynchelper:
                for response in tqdm(
                    asynchelper.generate_response(),
                    total=len(prompts),
                    desc="Progress",
                    unit=" inputs",
                    disable=hide_progressbar,
                ):
                    yield response
        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)

    def tokenize_as_completed(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        return_tokens: bool = False,
        options: Options = None,
    ) -> Generator[TokenizeResult]:
        """The tokenize endpoint allows you to check the conversion of provided prompts to tokens
        for a given model. It splits text into words or subwords, which then are converted to ids
        through a look-up table (vocabulary). Tokenization allows the model to have a reasonable
        vocabulary size.

        Args:
            return_tokens (bool, optional): Return tokens with the response. Defaults to False.

        Yields:
            Generator[TokenizeResult]: The Tokenized input
        """
        if len(prompts) > 0 and isinstance(prompts[0], PromptPattern):
            prompts = PromptPattern.list_str(prompts)

        try:
            params = TokenParams(return_tokens=return_tokens)
            for i in range(0, len(prompts), Metadata.DEFAULT_MAX_PROMPTS):
                tokenize_response = self.service.tokenize(
                    model=self.model,
                    inputs=prompts[i : min(i + Metadata.DEFAULT_MAX_PROMPTS, len(prompts))],
                    params=params,
                    options=options,
                )

                if tokenize_response.status_code == 200:
                    response_json = tokenize_response.json()
                    for y, result in enumerate(response_json["results"]):
                        result["input_text"] = prompts[i + y]
                    responses = TokenizeResponse(**response_json)
                    for token in responses.results:
                        yield token

                else:
                    raise GenAiException(tokenize_response)
        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)

    def tokenize(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        return_tokens: bool = False,
        options: Options = None,
    ) -> list[TokenizeResult]:
        """The tokenize endpoint allows you to check the conversion of provided prompts to tokens
        for a given model. It splits text into words or subwords, which then are converted to ids
        through a look-up table (vocabulary). Tokenization allows the model to have a reasonable
        vocabulary size.

        Args:
            prompts (list[str]): The list of one or more prompt strings.
            return_tokens (bool, optional): Return tokens with the response. Defaults to False.

        Returns:
            list[TokenizeResult]: The Tokenized input
        """
        return list(self.tokenize_as_completed(prompts, return_tokens, options=options))

    def tokenize_async(
        self,
        prompts: Union[list[str], list[PromptPattern]],
        ordered: bool = False,
        callback: Callable[[TokenizeResult], Any] = None,
        return_tokens: bool = False,
        options: Options = None,
    ) -> Generator[Union[TokenizeResult, None]]:
        """The tokenize endpoint allows you to check the conversion of provided prompts to tokens
        for a given model. It splits text into words or subwords, which then are converted to ids
        through a look-up table (vocabulary). Tokenization allows the model to have a reasonable
        vocabulary size. This python method utilizes async capabilities and returns
        responses as they arrive.

        Args:
            prompts (list[str]): The list of one or more prompt strings.
            ordered (bool): Whether the responses should be returned in-order.
            callback (Callable[[TokenizeResult], Any]): Callback to call for each result.
            return_tokens (bool, optional): Return tokens with the response. Defaults to False.

        Returns:
            Generator[Union[TokenizeResult, None]]: The Tokenized input
        """
        if len(prompts) > 0 and isinstance(prompts[0], PromptPattern):
            prompts = PromptPattern.list_str(prompts)

        logger.debug(f"Calling Tokenize Async. Prompts: {prompts}, params: {self.params}")

        try:
            params = TokenParams(return_tokens=return_tokens)
            with AsyncResponseGenerator(
                self.model,
                prompts,
                params,
                self.service,
                fn="tokenize",
                ordered=ordered,
                callback=callback,
                options=options,
            ) as asynchelper:
                for response in asynchelper.generate_response():
                    yield response
        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)

    def tune(
        self,
        name: str,
        method: str,
        task: str,
        hyperparameters: CreateTuneHyperParams = None,
        training_file_ids: list[str] = None,
        validation_file_ids: list[str] = None,
    ):
        """Tune the base-model for given training data.

        Args:
            name (str): Label for this tuned model.
            method (str): The list of one or more prompt strings.
            task (str): Task ID, could be "classification", "summarization", or "generation"
            hyperparameters (CreateTuneHyperParams): Tuning hyperparameters
            training_file_ids (list[str]): IDs for files with training data
            validation_file_ids (list[str]): IDs for files with validation data

        Returns:
            Model: An instance of tuned model
        """
        if training_file_ids is None:
            raise GenAiException(ValueError("Parameter should be specified: training_file_paths or training_file_ids."))

        params = CreateTuneParams(
            name=name,
            model_id=self.model,
            method_id=method,
            task_id=task,
            training_file_ids=training_file_ids,
            validation_file_ids=validation_file_ids,
            parameters=hyperparameters or CreateTuneHyperParams(),
        )
        tune = TuneManager.create_tune(service=self.service, params=params)
        return Model(model=tune.id, params=None, credentials=self.creds)

    def status(self):
        """Get status of the model, currently supports only tuned models.

        Returns:
            str: Status of a tuned model
        """
        params = TunesListParams()
        tunes = TuneManager.list_tunes(service=self.service, params=params).results
        id_to_status = {t.id: t.status for t in tunes}
        if self.model not in id_to_status:
            raise GenAiException(ValueError("Tuned model not found. Currently method supports only tuned models."))
        return id_to_status[self.model]

    def delete(self):
        params = TunesListParams()
        tunes = TuneManager.list_tunes(service=self.service, params=params).results
        id_to_status = {t.id: t.status for t in tunes}
        if self.model not in id_to_status:
            raise GenAiException(ValueError("Tuned model not found. Currently method supports only tuned models."))
        TuneManager.delete_tune(service=self.service, tune_id=self.model)
