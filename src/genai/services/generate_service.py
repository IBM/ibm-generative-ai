import ast
import json
from typing import Any, Callable, Generator, Optional, Union

from tqdm import tqdm

from genai.exceptions import GenAiException
from genai.metadata import Metadata
from genai.options import Options
from genai.prompt_pattern import PromptPattern
from genai.schemas import GenerateParams, TokenParams
from genai.schemas.responses import (
    GenerateResponse,
    GenerateResult,
    GenerateStreamResponse,
    logger,
)
from genai.services.async_generator import AsyncResponseGenerator
from genai.services.base_service import BaseService

Params = Union[GenerateParams, TokenParams, Any]


class GenerateService(BaseService):
    def generate_stream(
        self,
        model: str,
        params: Params,
        prompts: Union[list[str], list[PromptPattern]],
        options: Options = None,
    ) -> Generator[GenerateStreamResponse, None, None]:
        if len(prompts) > 0 and isinstance(prompts[0], PromptPattern):
            prompts = PromptPattern.list_str(prompts)

        params = params.copy()
        params.stream = True

        try:
            for i in range(0, len(prompts), Metadata.DEFAULT_MAX_PROMPTS):
                batch = prompts[i : min(i + Metadata.DEFAULT_MAX_PROMPTS, len(prompts))]

                response_gen = self._api_service.generate(
                    model, batch, params, options=options, streaming=True
                )

                for response in response_gen:
                    if not response:
                        continue

                    if "status_code" in response:
                        error = json.loads(response)
                        raise GenAiException(error)

                    try:
                        parsed_response = json.loads(response)
                        if "moderation" in parsed_response:
                            result = {
                                "id": parsed_response["id"],
                                "results": [],
                                "model_id": parsed_response["model_id"],
                                "created_at": parsed_response["created_at"],
                                "moderation": parsed_response["moderation"],
                            }
                            yield GenerateStreamResponse(**result)

                        for result in parsed_response["results"]:
                            yield GenerateStreamResponse(**result)

                    except Exception:
                        logger.error(
                            "Could not parse {} as literal_eval".format(response)
                        )

        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)

    def generate_as_completed(
        self,
        model: str,
        params: Params,
        prompts: Union[list[str], list[PromptPattern]],
        options: Options = None,
    ) -> Generator[GenerateResult, None, None]:
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

        params = params.copy()
        params.stream = False

        logger.debug(f"Calling Generate. Prompts: {prompts}, params: {params}")

        try:
            for i in range(0, len(prompts), Metadata.DEFAULT_MAX_PROMPTS):
                response_gen = self._api_service.generate(
                    model=model,
                    inputs=prompts[
                        i : min(i + Metadata.DEFAULT_MAX_PROMPTS, len(prompts))
                    ],
                    params=params,
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
        self,
        model: str,
        prompts: Union[list[str], list[PromptPattern]],
        params: Params,
        options: Optional[Options] = None,
    ) -> list[GenerateResult]:
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
        return list(self.generate_as_completed(model, params, prompts, options))

    def generate_async(
        self,
        model: str,
        prompts: Union[list[str], list[PromptPattern]],
        params: Params,
        ordered: bool = False,
        callback: Optional[Callable[[GenerateResult], Any]] = None,
        hide_progressbar: bool = False,
        options: Options = None,
        *,
        throw_on_error: bool = False,
    ) -> Generator[Union[GenerateResult, None], None, None]:
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

        params = params.copy()
        params.stream = False
        logger.debug(f"Calling Generate Async. Prompts: {prompts}, params: {params}")

        try:
            with AsyncResponseGenerator(
                model,
                prompts,
                params,
                self._api_service,
                ordered=ordered,
                callback=callback,
                options=options,
                throw_on_error=throw_on_error,
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
