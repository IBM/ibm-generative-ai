from typing import Generator, Optional, Union

import httpx
from httpx import AsyncClient, HTTPStatusError
from pydantic import BaseModel

from genai._types import ModelLike
from genai._utils.api_client import ApiClient
from genai._utils.async_executor import execute_async
from genai._utils.general import (
    prompts_to_strings,
    to_model_instance,
    to_model_optional,
)
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    CommonExecutionOptions,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    ModerationParameters,
    PromptTemplateData,
    TextGenerationComparisonCreateEndpoint,
    TextGenerationComparisonCreateRequestRequest,
    TextGenerationComparisonCreateResponse,
    TextGenerationComparisonParameters,
    TextGenerationCreateEndpoint,
    TextGenerationCreateResponse,
    TextGenerationParameters,
    TextGenerationStreamCreateEndpoint,
    TextGenerationStreamCreateResponse,
)
from genai.schema._api import (
    _TextGenerationComparisonCreateParametersQuery,
    _TextGenerationComparisonCreateRequest,
    _TextGenerationCreateParametersQuery,
    _TextGenerationCreateRequest,
    _TextGenerationStreamCreateParametersQuery,
    _TextGenerationStreamCreateRequest,
)
from genai.text.generation._generation_utils import generation_stream_handler
from genai.text.generation.feedback.feedback_service import FeedbackService as _FeedbackService
from genai.text.generation.limits.limit_service import LimitService as _LimitService

__all__ = ["GenerationService", "BaseConfig", "BaseServices", "CreateExecutionOptions"]

from genai._utils.http_client.retry_transport import BaseRetryTransport
from genai._utils.limiters.base_limiter import BaseLimiter
from genai._utils.limiters.external_limiter import ConcurrencyResponse, ExternalLimiter
from genai._utils.limiters.local_limiter import LocalLimiter
from genai._utils.limiters.shared_limiter import LoopBoundLimiter


class BaseServices(BaseServiceServices):
    LimitService: type[_LimitService] = _LimitService
    FeedbackService: type[_FeedbackService] = _FeedbackService


class CreateExecutionOptions(BaseModel):
    throw_on_error: CommonExecutionOptions.throw_on_error = True
    ordered: CommonExecutionOptions.ordered = True
    concurrency_limit: CommonExecutionOptions.concurrency_limit = None
    batch_size: CommonExecutionOptions.batch_size = None
    rate_limit_options: CommonExecutionOptions.rate_limit_options = None
    callback: CommonExecutionOptions.callback[
        Union[TextGenerationStreamCreateResponse, TextGenerationCreateResponse]
    ] = None


class BaseConfig(BaseServiceConfig):
    create_execution_options: CreateExecutionOptions = CreateExecutionOptions()


class GenerationService(BaseService[BaseConfig, BaseServices]):
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
        self.feedback = services.FeedbackService(api_client=api_client)
        self.limit = services.LimitService(api_client=api_client)

    def _get_concurrency_limiter(self) -> LoopBoundLimiter:
        async def handler():
            response = await self.limit.aretrieve()
            return ConcurrencyResponse(
                limit=response.result.concurrency.limit,
                remaining=response.result.concurrency.remaining,
            )

        return LoopBoundLimiter(lambda: ExternalLimiter(handler=handler))

    @set_service_action_metadata(endpoint=TextGenerationCreateEndpoint)
    def create(
        self,
        *,
        model_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        inputs: Optional[Union[list[str], str]] = None,
        parameters: Optional[ModelLike[TextGenerationParameters]] = None,
        moderations: Optional[ModelLike[ModerationParameters]] = None,
        data: Optional[ModelLike[PromptTemplateData]] = None,
        execution_options: Optional[ModelLike[CreateExecutionOptions]] = None,
    ) -> Generator[TextGenerationCreateResponse, None, None]:
        """
        Args:
            model_id: The ID of the model.
            prompt_id: The ID of the prompt which should be used.
            inputs: Prompt/prompts to process. It is recommended not to leave any trailing spaces.
            parameters: Parameters for text generation.
            moderations: Parameters for moderation.
            data: An optional data object for underlying prompt.
            execution_options: An optional configuration how SDK should work (error handling, limits, callbacks, ...)

        Yields:
            TextGenerationCreateResponse object (server response without modification).

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.

        Note:
            To limit number of concurrent requests or change execution procedure, see 'execute_options' parameter.
        """
        metadata = get_service_action_metadata(self.create)
        prompts: list[str] = prompts_to_strings(inputs)
        parameters_formatted = to_model_optional(parameters, TextGenerationParameters)
        moderations_formatted = to_model_optional(moderations, ModerationParameters)
        template_formatted = to_model_optional(data, PromptTemplateData)
        execution_options_formatted = to_model_instance(
            [self.config.create_execution_options, execution_options], CreateExecutionOptions
        )
        assert execution_options_formatted

        self._log_method_execution(
            "Generate Create",
            prompts=prompts,
            prompt_id=prompt_id,
            parameters=parameters_formatted,
            moderations=moderations_formatted,
            data=template_formatted,
            execution_options=execution_options_formatted,
        )

        if prompt_id is not None:
            with self._get_http_client() as client:
                http_response = client.post(
                    url=self._get_endpoint(metadata.endpoint),
                    params=_TextGenerationCreateParametersQuery().model_dump(),
                    json=_TextGenerationCreateRequest(
                        input=None,
                        model_id=model_id,
                        moderations=moderations_formatted,
                        parameters=parameters_formatted,
                        prompt_id=prompt_id,
                        data=template_formatted,
                    ).model_dump(),
                )
                yield TextGenerationCreateResponse(**http_response.json())
                return

        async def handler(input: str, http_client: AsyncClient, limiter: BaseLimiter) -> TextGenerationCreateResponse:
            self._log_method_execution("Generate Create - processing input", input=input)

            async def handle_retry(ex: HTTPStatusError):
                if ex.response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                    await limiter.report_error()

            async def handle_success(*args):
                await limiter.report_success()

            http_response = await http_client.post(
                url=self._get_endpoint(metadata.endpoint),
                extensions={
                    BaseRetryTransport.Callback.Retry: handle_retry,
                    BaseRetryTransport.Callback.Success: handle_success,
                },
                params=_TextGenerationCreateParametersQuery().model_dump(),
                json=_TextGenerationCreateRequest(
                    input=input,
                    model_id=model_id,
                    moderations=moderations_formatted,
                    parameters=parameters_formatted,
                    prompt_id=prompt_id,
                    data=template_formatted,
                ).model_dump(),
            )
            response = TextGenerationCreateResponse(**http_response.json())

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

    @set_service_action_metadata(endpoint=TextGenerationStreamCreateEndpoint)
    def create_stream(
        self,
        *,
        input: Optional[str] = None,
        model_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        parameters: Optional[ModelLike[TextGenerationParameters]] = None,
        moderations: Optional[ModelLike[ModerationParameters]] = None,
        data: Optional[ModelLike[PromptTemplateData]] = None,
    ) -> Generator[TextGenerationStreamCreateResponse, None, None]:
        """
        Yields:
            TextGenerationStreamCreateResponse (raw server response object)

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        metadata = get_service_action_metadata(self.create_stream)
        parameters_formatted = to_model_optional(parameters, TextGenerationParameters)
        moderations_formatted = to_model_optional(moderations, ModerationParameters)
        template_formatted = to_model_optional(data, PromptTemplateData)

        self._log_method_execution(
            "Generate Create Stream",
            input=input,
            parameters=parameters_formatted,
            moderations=moderations_formatted,
            template=template_formatted,
        )

        with self._get_http_client() as client:
            yield from generation_stream_handler(
                ResponseModel=TextGenerationStreamCreateResponse,
                logger=self._logger,
                generator=client.post_stream(
                    url=self._get_endpoint(metadata.endpoint),
                    params=_TextGenerationStreamCreateParametersQuery().model_dump(),
                    json=_TextGenerationStreamCreateRequest(
                        input=input,
                        parameters=parameters_formatted,
                        model_id=model_id,
                        prompt_id=prompt_id,
                        moderations=moderations_formatted,
                        data=template_formatted,
                    ).model_dump(),
                ),
            )

    @set_service_action_metadata(endpoint=TextGenerationComparisonCreateEndpoint)
    def compare(
        self,
        *,
        request: TextGenerationComparisonCreateRequestRequest,
        compare_parameters: Optional[ModelLike[TextGenerationComparisonParameters]] = None,
        name: Optional[str] = None,
    ) -> TextGenerationComparisonCreateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        metadata = get_service_action_metadata(self.compare)
        request_formatted = to_model_instance(request, TextGenerationComparisonCreateRequestRequest)
        compare_parameters_formatted = to_model_instance(compare_parameters, TextGenerationComparisonParameters)

        self._log_method_execution(
            "Text Generation Compare",
            input=input,
            requests=request_formatted,
            parameters=compare_parameters_formatted,
        )

        with self._get_http_client() as client:
            http_response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextGenerationComparisonCreateParametersQuery().model_dump(),
                json=_TextGenerationComparisonCreateRequest(
                    name=name,
                    compare_parameters=compare_parameters_formatted,
                    request=request_formatted,
                ).model_dump(),
            )
            return TextGenerationComparisonCreateResponse(**http_response.json())

    def _get_local_limiter(self, limit: Optional[int]):
        return LoopBoundLimiter(lambda: LocalLimiter(limit=limit)) if limit else None
