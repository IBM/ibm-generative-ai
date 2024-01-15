from typing import Generator, Optional, Sequence, Union

from genai._generated.api import (
    TextChatCreateParametersQuery,
    TextChatCreateRequest,
    TextChatStreamCreateRequest,
    TextGenerationStreamCreateParametersQuery,
)
from genai._generated.endpoints import (
    TextChatCreateEndpoint,
    TextChatStreamCreateEndpoint,
)
from genai._types import EnumLike, ModelLike
from genai._utils.api_client import ApiClient
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai._utils.general import to_enum_optional, to_model_instance, to_model_optional
from genai.request.request_service import RequestService as _RequestService
from genai.text.chat.schema import (
    BaseMessage,
    ModerationParameters,
    TextChatCreateResponse,
    TextChatStreamCreateResponse,
    TextGenerationParameters,
    TrimMethod,
)
from genai.text.generation._generation_utils import generation_stream_handler

__all__ = ["ChatService", "BaseServices"]


class BaseServices(BaseServiceServices):
    RequestService: type[_RequestService] = _RequestService


class ChatService(BaseService[BaseServiceConfig, BaseServices]):
    Services = BaseServices

    def __init__(
        self,
        *,
        api_client: ApiClient,
        config: Optional[Union[BaseServiceConfig, dict]] = None,
        services: Optional[BaseServices] = None,
    ):
        super().__init__(api_client=api_client, config=config)
        if not services:
            services = BaseServices()

        self._request = services.RequestService(api_client=api_client)

    def create(
        self,
        *,
        conversation_id: Optional[str] = None,
        model_id: Optional[str] = None,
        messages: Optional[Sequence[BaseMessage]] = None,
        moderations: Optional[ModelLike[ModerationParameters]] = None,
        parameters: Optional[ModelLike[TextGenerationParameters]] = None,
        parent_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        prompt_template_id: Optional[str] = None,
        trim_method: Optional[EnumLike[TrimMethod]] = None,
        use_conversation_parameters: Optional[bool] = None,
    ) -> TextChatCreateResponse:
        """
        Example::

            from genai import Client, Credentials
            from genai.text.chat import HumanMessage, TextGenerationParameters

            client = Client(credentials=Credentials.from_env())

            # Create a new conversation
            response = client.text.chat.create(
                model_id="meta-llama/llama-2-70b-chat",
                messages=[HumanMessage(content="Describe the game Chess?")],
                parameters=TextGenerationParameters(max_token_limit=100)
            )
            conversation_id = response.conversation_id
            print(f"Response: {response.results[0].generated_text}")

            # Continue in the conversation
            response = client.text.chat.create(
                conversation_id=conversation_id,
                use_conversation_parameters=True,
                messages=[HumanMessage(content="Who is the best player of that game?")]
            )
            print(f"Response: {response.results[0].generated_text}")

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_body = TextChatCreateRequest(
            model_id=model_id,
            conversation_id=conversation_id,
            messages=self._prepare_messages(messages) if messages is not None else None,
            moderations=to_model_optional(moderations, ModerationParameters),
            parameters=to_model_optional(parameters, TextGenerationParameters),
            parent_id=parent_id,
            prompt_id=prompt_id,
            prompt_template_id=prompt_template_id,
            trim_method=to_enum_optional(trim_method, TrimMethod),
            use_conversation_parameters=use_conversation_parameters or None,
        ).model_dump()

        self._log_method_execution("Text Chat Generation Create", **request_body)

        with self._get_http_client() as client:
            http_response = client.post(
                url=self._get_endpoint(TextChatCreateEndpoint),
                params=TextChatCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return TextChatCreateResponse(**http_response.json())

    def create_stream(
        self,
        *,
        model_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        messages: Optional[list[BaseMessage]] = None,
        moderations: Optional[ModelLike[ModerationParameters]] = None,
        parameters: Optional[ModelLike[TextGenerationParameters]] = None,
        parent_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        prompt_template_id: Optional[str] = None,
        trim_method: Optional[EnumLike[TrimMethod]] = None,
        use_conversation_parameters: Optional[bool] = None,
    ) -> Generator[TextChatStreamCreateResponse, None, None]:
        """
        Example::

            from genai import Client, Credentials
            from genai.text.chat import HumanMessage, TextGenerationParameters

            client = Client(credentials=Credentials.from_env())

            # Create a new conversation
            for response in client.text.chat.create_stream(
                    model_id="meta-llama/llama-2-70b-chat",
                    messages=[HumanMessage(content="Describe the game Chess?")],
                    parameters=TextGenerationParameters(max_token_limit=100)
                ):
                print(f"Chunk retrieved: {response.results[0].generated_text}")

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_body = TextChatStreamCreateRequest(
            model_id=model_id,
            conversation_id=conversation_id,
            messages=self._prepare_messages(messages) if messages is not None else None,
            moderations=to_model_optional(moderations, ModerationParameters),
            parameters=to_model_optional(parameters, TextGenerationParameters),
            parent_id=parent_id,
            prompt_id=prompt_id,
            prompt_template_id=prompt_template_id,
            trim_method=to_enum_optional(trim_method, TrimMethod),
            use_conversation_parameters=use_conversation_parameters or None,
        ).model_dump()

        self._log_method_execution("Text Chat Generation Create Stream", **request_body)

        with self._get_http_client() as client:
            yield from generation_stream_handler(
                ResponseModel=TextChatStreamCreateResponse,
                logger=self._logger,
                generator=client.post_stream(
                    url=self._get_endpoint(TextChatStreamCreateEndpoint),
                    params=TextGenerationStreamCreateParametersQuery().model_dump(),
                    json=request_body,
                ),
            )

    def _prepare_messages(self, messages: Sequence[Union[BaseMessage, dict]]) -> list[BaseMessage]:
        return [to_model_instance(msg, BaseMessage) for msg in messages]
