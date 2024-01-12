from typing import Generator, Optional, Union

import httpx
from httpx import AsyncClient, HTTPStatusError
from pydantic import BaseModel

from genai._generated.api import (
    TextEmbeddingCreateParametersQuery,
    TextEmbeddingCreateRequest,
)
from genai._generated.endpoints import TextEmbeddingCreateEndpoint
from genai._types import ModelLike
from genai._utils.api_client import ApiClient
from genai._utils.async_executor import execute_async
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai._utils.general import cast_list, to_model_instance
from genai._utils.shared_options import CommonExecutionOptions
from genai.text.embedding.limit.limit_service import LimitService
from genai.text.embedding.schema import TextEmbeddingCreateResponse

__all__ = ["EmbeddingService", "BaseConfig", "BaseServices", "CreateExecutionOptions"]

from genai._utils.http_client.retry_transport import BaseRetryTransport
from genai._utils.limiters.base_limiter import BaseLimiter
from genai._utils.limiters.external_limiter import ConcurrencyResponse, ExternalLimiter
from genai._utils.limiters.local_limiter import LocalLimiter
from genai._utils.limiters.shared_limiter import LoopBoundLimiter


class BaseServices(BaseServiceServices):
    LimitService: type[LimitService] = LimitService


class CreateExecutionOptions(BaseModel):
    throw_on_error: CommonExecutionOptions.throw_on_error = True
    ordered: CommonExecutionOptions.ordered = True
    concurrency_limit: CommonExecutionOptions.concurrency_limit = None
    callback: CommonExecutionOptions.callback[TextEmbeddingCreateResponse] = None


class BaseConfig(BaseServiceConfig):
    create_execution_options: CreateExecutionOptions = CreateExecutionOptions()


class EmbeddingService(BaseService[BaseConfig, BaseServices]):
    Config = BaseConfig
    Services = BaseServices

    def __init__(
        self,
        *,
        api_client: ApiClient,
        services: Optional[BaseServices] = None,
        config: Optional[Union[BaseConfig, dict]] = None,
    ):
        super().__init__(api_client=api_client, config=config)

        if not services:
            services = BaseServices()

        self._concurrency_limiter = self._get_concurrency_limiter()
        self.limit = services.LimitService(api_client=api_client)

    def create(
        self,
        *,
        model_id: str,
        inputs: Union[str, list[str]],
        execution_options: Optional[ModelLike[CreateExecutionOptions]] = None,
    ) -> Generator[TextEmbeddingCreateResponse, None, None]:
        """
        Creates embedding vectors from an input(s).

        Example::

            from genai import Client, Credentials
            from genai.text.chat import HumanMessage, TextGenerationParameters

            client = Client(credentials=Credentials.from_env())

            # Create a new conversation
            response = client.text.embedding.create(
                model_id="sentence-transformers/all-minilm-l6-v2",
                input="Write a tagline for an alumni association: Together we"
            )
            print("Output vectors", response.results)

        Yields:
            TextEmbeddingCreateResponse object.

        Raises:
            ApiResponseException: If case of an API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        prompts: list[str] = cast_list(inputs)
        execution_options_formatted = to_model_instance(
            [self.config.create_execution_options, execution_options], CreateExecutionOptions
        )
        assert execution_options_formatted

        self._log_method_execution(
            "Embedding Create",
            prompts=prompts,
            execution_options=execution_options_formatted,
        )

        async def handler(input: str, http_client: AsyncClient, limiter: BaseLimiter) -> TextEmbeddingCreateResponse:
            self._log_method_execution("Embedding Create - processing input", input=input)

            async def handle_retry(ex: HTTPStatusError):
                if ex.response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                    await limiter.report_error()

            async def handle_success(*args):
                await limiter.report_success()

            http_response = await http_client.post(
                url=self._get_endpoint(TextEmbeddingCreateEndpoint),
                extensions={
                    BaseRetryTransport.Callback.Retry: handle_retry,
                    BaseRetryTransport.Callback.Success: handle_success,
                },
                params=TextEmbeddingCreateParametersQuery().model_dump(),
                json=TextEmbeddingCreateRequest(input=input, model_id=model_id).model_dump(),
            )
            response = TextEmbeddingCreateResponse(**http_response.json())

            if execution_options_formatted.callback:
                execution_options_formatted.callback(response)

            return response

        yield from execute_async(
            inputs=prompts,
            handler=handler,
            limiters=[
                self._concurrency_limiter,
                self._get_local_limiter(execution_options_formatted.concurrency_limit),
            ],
            http_client=self._get_async_http_client,
            ordered=execution_options_formatted.ordered,
            throw_on_error=execution_options_formatted.throw_on_error,
        )

    def _get_local_limiter(self, limit: Optional[int]):
        return LoopBoundLimiter(lambda: LocalLimiter(limit=limit)) if limit else None

    def _get_concurrency_limiter(self) -> LoopBoundLimiter:
        async def handler():
            response = await self.limit.aretrieve()
            return ConcurrencyResponse(
                limit=response.result.concurrency.limit,
                remaining=response.result.concurrency.remaining,
            )

        return LoopBoundLimiter(lambda: ExternalLimiter(handler=handler))
