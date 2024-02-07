from datetime import datetime
from typing import Optional, TypeVar, Union

from pydantic import BaseModel

from genai._types import EnumLike
from genai._utils.general import cast_list, to_enum, to_enum_optional
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import (
    RequestApiVersion,
    RequestChatConversationIdRetrieveResponse,
    RequestEndpoint,
    RequestOrigin,
    RequestRetrieveResponse,
    RequestStatus,
)
from genai.schema._api import (
    _RequestChatConversationIdDeleteParametersQuery,
    _RequestChatConversationIdRetrieveParametersQuery,
    _RequestIdDeleteParametersQuery,
    _RequestRetrieveParametersQuery,
)
from genai.schema._endpoints import (
    RequestChatConversationIdDeleteEndpoint,
    RequestChatConversationIdRetrieveEndpoint,
    RequestIdDeleteEndpoint,
    RequestRetrieveEndpoint,
)

T = TypeVar("T", bound=BaseModel)

__all__ = ["RequestService"]


class RequestService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=RequestChatConversationIdRetrieveEndpoint)
    def chat(self, conversation_id: str) -> RequestChatConversationIdRetrieveResponse:
        """
        Args:
            conversation_id: The ID of the conversation to retrieve.

        Raises:
            ValueError: If the ID is an empty string.
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(conversation_id)
        self._log_method_execution("Requests Chat", conversation_id=conversation_id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.chat)
            http_response = client.get(
                url=self._get_endpoint(metadata.endpoint, conversationId=conversation_id),
                params=_RequestChatConversationIdRetrieveParametersQuery().model_dump(),
            )
            return RequestChatConversationIdRetrieveResponse(**http_response.json())

    @set_service_action_metadata(endpoint=RequestChatConversationIdDeleteEndpoint)
    def chat_delete(self, conversation_id: str) -> None:
        """
        Args:
            conversation_id: The ID of the conversation to delete.

        Raises:
            ValueError: If the ID is an empty string.
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(conversation_id)
        self._log_method_execution("Request Delete Chat", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.chat_delete)
            client.delete(
                url=self._get_endpoint(metadata.endpoint, conversationId=conversation_id),
                params=_RequestChatConversationIdDeleteParametersQuery().model_dump(),
            )

    @set_service_action_metadata(endpoint=RequestRetrieveEndpoint)
    def list(
        self,
        *,
        api: Optional[RequestApiVersion] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[EnumLike[RequestStatus]] = None,
        origin: Optional[EnumLike[RequestOrigin]] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        endpoint: Optional[Union[RequestEndpoint, list[RequestEndpoint]]] = None,
        date: Optional[datetime] = None,
    ) -> RequestRetrieveResponse:
        """
        Lists requests based on the given parameters.

        Raises:
            ValueError: If the ID is an empty string.
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        params = _RequestRetrieveParametersQuery(
            limit=limit,
            offset=offset,
            status=to_enum_optional(status, RequestStatus),
            origin=to_enum_optional(origin, RequestOrigin),
            before=before,
            after=after,
            api=to_enum_optional(api, RequestApiVersion),
            date=date,
            endpoint=(
                [to_enum(RequestEndpoint, e) for e in cast_list(endpoint) if e is not None] if endpoint else None
            ),
        ).model_dump()

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.list)
            http_response = client.get(url=self._get_endpoint(metadata.endpoint), params=params)
            return RequestRetrieveResponse(**http_response.json())

    @set_service_action_metadata(endpoint=RequestIdDeleteEndpoint)
    def delete(self, id: str) -> None:
        """
        Deletes request with the given ID.

        Raises:
            ValueError: If the ID is an empty string.
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Request Delete", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.delete)
            client.delete(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_RequestIdDeleteParametersQuery().model_dump(),
            )
