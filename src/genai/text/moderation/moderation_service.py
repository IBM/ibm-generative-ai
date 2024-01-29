from typing import Generator, Optional, Union

from genai._types import ModelLike
from genai._utils.async_executor import execute_async
from genai._utils.general import (
    prompts_to_strings,
    to_model_instance,
    to_model_optional,
)
from genai._utils.http_client.httpx_client import AsyncHttpxClient
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    CommonExecutionOptions,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    HAPOptions,
    ImplicitHateOptions,
    StigmaOptions,
    TextModerationCreateEndpoint,
    TextModerationCreateResponse,
)
from genai.schema._api import (
    _TextModerationCreateParametersQuery,
    _TextModerationCreateRequest,
)

__all__ = ["ModerationService", "BaseConfig", "CreateExecutionOptions"]


class CreateExecutionOptions(BaseServiceConfig):
    throw_on_error: CommonExecutionOptions.throw_on_error = True
    ordered: CommonExecutionOptions.ordered = True


class BaseConfig(BaseServiceConfig):
    create_execution_options: CreateExecutionOptions = CreateExecutionOptions()


class ModerationService(BaseService[BaseConfig, BaseServiceServices]):
    Config = BaseConfig

    @set_service_action_metadata(endpoint=TextModerationCreateEndpoint)
    def create(
        self,
        inputs: Union[str, list[str]],
        *,
        hap: Optional[ModelLike[HAPOptions]] = None,
        implicit_hate: Optional[ModelLike[ImplicitHateOptions]] = None,
        stigma: Optional[ModelLike[StigmaOptions]] = None,
        execution_options: Optional[ModelLike[CreateExecutionOptions]] = None,
    ) -> Generator[TextModerationCreateResponse, None, None]:
        """
        Args:
            inputs: Prompt/Prompts for text moderation.
            hap: HAP configuration (hate, abuse, profanity).
            implicit_hate: Implicit Hate configuration.
            stigma: Stigma configuration.
            execution_options: Configuration processing.

        Example:
            from genai import Client, Credentials
            from genai.text.moderation import HAPOptions

            client = Client(credentials=Credentials.from_env())
            inputs = ["First input", "Second input"]
            counter = 0

            for response in client.text.moderation.create(inputs=inputs, hap=HAPOptions(threshold=0.65)):
                for result in response.results:
                    input = inputs[counter]
                    counter += 1
                    print(f"Response for {input}", result.hap)

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        metadata = get_service_action_metadata(self.create)
        execution_options_formatted = to_model_instance(
            [self.config.create_execution_options, execution_options], CreateExecutionOptions
        )
        self._log_method_execution(
            "Moderation Create",
            prompts=inputs,
            hap=hap,
            implicit_hate=implicit_hate,
            stigma=stigma,
            execution_options=execution_options_formatted,
        )

        async def handler(input: str, http_client: AsyncHttpxClient, *_) -> TextModerationCreateResponse:
            self._log_method_execution("Moderation Create - processing input", input=input)

            http_response = await http_client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextModerationCreateParametersQuery().model_dump(),
                json=_TextModerationCreateRequest(
                    input=input,
                    hap=to_model_optional(hap, HAPOptions),
                    implicit_hate=to_model_optional(hap, ImplicitHateOptions),
                    stigma=to_model_optional(stigma, StigmaOptions),
                ).model_dump(),
            )
            return TextModerationCreateResponse(**http_response.json())

        yield from execute_async(
            inputs=prompts_to_strings(inputs),
            handler=handler,
            http_client=self._get_async_http_client,
            ordered=execution_options_formatted.ordered,
            throw_on_error=execution_options_formatted.throw_on_error,
        )
