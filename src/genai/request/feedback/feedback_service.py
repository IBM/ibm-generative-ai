from typing import Optional, TypeVar

from pydantic import BaseModel

from genai._types import EnumLike
from genai._utils.general import to_enum, to_enum_optional
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import (
    RequestFeedbackCategory,
    RequestFeedbackVote,
    RequestIdFeedbackCreateEndpoint,
    RequestIdFeedbackCreateResponse,
    RequestIdFeedbackRetrieveEndpoint,
    RequestIdFeedbackRetrieveResponse,
    RequestIdFeedbackUpdateEndpoint,
    RequestIdFeedbackUpdateResponse,
)
from genai.schema._api import (
    _RequestIdFeedbackCreateParametersQuery,
    _RequestIdFeedbackCreateRequest,
    _RequestIdFeedbackRetrieveParametersQuery,
    _RequestIdFeedbackUpdateParametersQuery,
    _RequestIdFeedbackUpdateRequest,
)

T = TypeVar("T", bound=BaseModel)

__all__ = ["FeedbackService"]


class FeedbackService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=RequestIdFeedbackRetrieveEndpoint)
    def retrieve(
        self,
        request_id: str,
    ) -> RequestIdFeedbackRetrieveResponse:
        """
        Retrieve feedback for the request.

        Raises:
            ApiResponseException: If target feedback does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        metadata = get_service_action_metadata(self.retrieve)
        assert_is_not_empty_string(request_id)
        self._log_method_execution("Request Feedback Retrieve", request_id=request_id)

        with self._get_http_client() as client:
            http_response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=request_id),
                params=_RequestIdFeedbackRetrieveParametersQuery().model_dump(),
            )
            return RequestIdFeedbackRetrieveResponse(**http_response.json())

    @set_service_action_metadata(endpoint=RequestIdFeedbackCreateEndpoint)
    def create(
        self,
        request_id: str,
        *,
        categories: Optional[list[EnumLike[RequestFeedbackCategory]]] = None,
        comment: Optional[str] = None,
        contact_consent: Optional[bool] = None,
        vote: Optional[EnumLike[RequestFeedbackVote]] = None,
    ) -> RequestIdFeedbackCreateResponse:
        """
        Provide feedback on the request.

        Args:
            request_id: A string representing the ID of the request.
            categories: An optional list of enum-like objects representing the feedback categories.
            comment: An optional string representing the feedback comment.
            contact_consent: Can we contact you for more information?
            vote: Either 'up' or 'down'.

        Raises:
            ApiResponseException: If target feedback does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(request_id)
        request_body = _RequestIdFeedbackCreateRequest(
            comment=comment,
            categories=(
                [to_enum(RequestFeedbackCategory, category) for category in categories]
                if categories is not None
                else None
            ),
            vote=to_enum_optional(vote, RequestFeedbackVote),
            contact_consent=contact_consent,
        ).model_dump()
        self._log_method_execution("Request Feedback Create", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            http_response = client.post(
                url=self._get_endpoint(metadata.endpoint, id=request_id),
                params=_RequestIdFeedbackCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return RequestIdFeedbackCreateResponse(**http_response.json())

    @set_service_action_metadata(endpoint=RequestIdFeedbackUpdateEndpoint)
    def update(
        self,
        request_id: str,
        *,
        categories: Optional[list[RequestFeedbackCategory]] = None,
        comment: Optional[str] = None,
        contact_consent: Optional[bool] = None,
        vote: Optional[EnumLike[RequestFeedbackVote]] = None,
    ) -> RequestIdFeedbackUpdateResponse:
        """
        Update existing feedback.

        Args:
            request_id: The ID of the request to update.
            categories: Optional. List of request feedback categories.
            comment: Optional. Comment for the request feedback.
            contact_consent: Can we contact you for more information?
            vote: Either 'up' or 'down'.

        Raises:
            ApiResponseException: If target feedback does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(request_id)
        request_body = _RequestIdFeedbackUpdateRequest(
            comment=comment,
            categories=categories,
            vote=to_enum_optional(vote, RequestFeedbackVote),
            contact_consent=contact_consent,
        ).model_dump()
        self._log_method_execution(
            "Request Feedback Update", request_id=request_id, categories=categories, comment=comment
        )

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.update)
            http_response = client.put(
                url=self._get_endpoint(metadata.endpoint, id=request_id),
                params=_RequestIdFeedbackUpdateParametersQuery().model_dump(),
                json=request_body,
            )
            return RequestIdFeedbackUpdateResponse(**http_response.json())
