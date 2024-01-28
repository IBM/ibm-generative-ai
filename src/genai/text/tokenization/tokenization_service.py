from typing import Generator, Optional, Union

from genai._types import ModelLike
from genai._utils.async_executor import execute_async
from genai._utils.general import (
    batch_by_size_constraint,
    cast_list,
    merge_objects,
    prompts_to_strings,
    to_model_instance,
)
from genai._utils.http_client.httpx_client import AsyncHttpxClient
from genai._utils.limiters.local_limiter import LocalLimiter
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    CommonExecutionOptions,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    TextTokenizationCreateEndpoint,
    TextTokenizationCreateResponse,
    TextTokenizationParameters,
)
from genai.schema._api import (
    _TextTokenizationCreateParametersQuery,
    _TextTokenizationCreateRequest,
)

__all__ = ["CreateExecutionOptions", "BaseConfig", "TokenizationService"]

from genai._utils.limiters.shared_limiter import LoopBoundLimiter


class CreateExecutionOptions(BaseServiceConfig):
    """Execution options for tokenization process."""

    throw_on_error: CommonExecutionOptions.throw_on_error = True
    ordered: CommonExecutionOptions.ordered = True
    concurrency_limit: CommonExecutionOptions.concurrency_limit = None
    batch_size: CommonExecutionOptions.batch_size = None
    rate_limit_options: CommonExecutionOptions.rate_limit_options = None
    callback: CommonExecutionOptions.callback[TextTokenizationCreateResponse] = None


class BaseConfig(BaseServiceConfig):
    create_execution_options: CreateExecutionOptions = CreateExecutionOptions()


class TokenizationService(BaseService[BaseConfig, BaseServiceServices]):
    Config = BaseConfig

    @set_service_action_metadata(endpoint=TextTokenizationCreateEndpoint)
    def create(
        self,
        *,
        input: Union[str, list[str]],
        model_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        parameters: Optional[ModelLike[TextTokenizationParameters]] = None,
        execution_options: Optional[ModelLike[CreateExecutionOptions]] = None,
    ) -> Generator[TextTokenizationCreateResponse, None, None]:
        """
        Args:
            input: The input data for tokenization. It can be a single string or a list of strings.
            model_id: The ID of the model to use for tokenization. Eiter 'model_id' or 'prompt_id' must be provided.
            prompt_id: The ID of the prompt to use for tokenization.  Eiter 'model_id' or 'prompt_id' must be provided.
            parameters: The parameters for tokenization, like return options.
            execution_options: The execution options for tokenization like batch size, callbacks and cetra.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        metadata = get_service_action_metadata(self.create)
        prompts = cast_list(input)
        options = to_model_instance([self.config.create_execution_options, execution_options], CreateExecutionOptions)
        parameters_validated = to_model_instance(parameters, TextTokenizationParameters)
        batches = batch_by_size_constraint(
            prompts_to_strings(prompts),
            max_size_bytes=self._api_client.config.max_payload_size_bytes,
            max_chunk_size=options.batch_size or len(prompts),
        )

        self._log_method_execution(
            "Tokenization Create",
            prompts=prompts,
            parameters=parameters_validated,
            options=options,
        )

        async def handler(inputs_chunk: list[str], http_client: AsyncHttpxClient, *_) -> TextTokenizationCreateResponse:
            http_response = await http_client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextTokenizationCreateParametersQuery().model_dump(),
                json=_TextTokenizationCreateRequest(
                    input=inputs_chunk,
                    model_id=model_id,
                    prompt_id=prompt_id,
                    parameters=parameters_validated,
                ).model_dump(),
            )
            response = TextTokenizationCreateResponse(**http_response.json())

            if options.callback:
                options.callback(response)

            return response

        yield from execute_async(
            inputs=list(batches),
            handler=handler,
            ordered=options.ordered,
            limiters=[self._get_local_limiter(options.concurrency_limit)],
            throw_on_error=options.throw_on_error,
            http_client=lambda: self._get_async_http_client(
                rate_limit_options=merge_objects(
                    {"max_rate": 25, "time_period": 1, "disable_rate_limit_no_header": True},
                    options.rate_limit_options,
                )
            ),
        )

    def _get_local_limiter(self, limit: Optional[int]):
        return LoopBoundLimiter(lambda: LocalLimiter(limit=limit)) if limit else None
