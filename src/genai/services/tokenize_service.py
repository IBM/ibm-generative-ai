import logging
from typing import Any, Callable, Generator, Optional, Union

from genai.exceptions import GenAiException
from genai.metadata import Metadata
from genai.options import Options
from genai.prompt_pattern import PromptPattern
from genai.schemas import TokenizeResult, TokenParams
from genai.schemas.responses import TokenizeResponse
from genai.services import AsyncResponseGenerator
from genai.services.base_service import BaseService

logger = logging.getLogger(__name__)


class TokenizeService(BaseService):
    def __call__(self, *args, **kwargs):
        return self.tokenize(*args, **kwargs)

    def tokenize(
        self,
        model_id: str,
        prompts: Union[list[str], list[PromptPattern]],
        params: Optional[TokenParams] = None,
        options: Optional[Options] = None,
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
        return list(
            self.tokenize_as_completed(model_id, prompts, params, options=options)
        )

    def tokenize_as_completed(
        self,
        model_id: str,
        prompts: Union[list[str], list[PromptPattern]],
        params: Optional[TokenParams] = None,
        options: Optional[Options] = None,
    ) -> Generator[TokenizeResult, None, None]:
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
            params = params or TokenParams(return_tokens=False)
            for i in range(0, len(prompts), Metadata.DEFAULT_MAX_PROMPTS):
                tokenize_response = self._api_service.tokenize(
                    model=model_id,
                    inputs=prompts[
                        i : min(i + Metadata.DEFAULT_MAX_PROMPTS, len(prompts))
                    ],
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

    def tokenize_async(
        self,
        model_id: str,
        prompts: Union[list[str], list[PromptPattern]],
        ordered: bool = False,
        callback: Optional[Callable[[TokenizeResult], Any]] = None,
        return_tokens: bool = False,
        options: Optional[Options] = None,
    ) -> Generator[Union[TokenizeResult, None], None, None]:
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
            options: (Options, optional): Extra optional top-level properties like (prompt_id).

        Returns:
            Generator[Union[TokenizeResult, None]]: The Tokenized input
        """
        if len(prompts) > 0 and isinstance(prompts[0], PromptPattern):
            prompts = PromptPattern.list_str(prompts)

        logger.debug(f"Calling Tokenize Async. Prompts: {prompts}")

        try:
            params = TokenParams(return_tokens=return_tokens)
            with AsyncResponseGenerator(
                model_id,
                prompts,
                params,
                self._api_service,
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
