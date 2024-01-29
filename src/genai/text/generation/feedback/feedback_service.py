from typing import Optional, TypeVar

from pydantic import BaseModel

from genai._types import EnumLike
from genai._utils.general import to_enum
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import (
    TextGenerationFeedbackCategory,
    TextGenerationIdFeedbackCreateEndpoint,
    TextGenerationIdFeedbackCreateResponse,
    TextGenerationIdFeedbackRetrieveEndpoint,
    TextGenerationIdFeedbackRetrieveResponse,
    TextGenerationIdFeedbackUpdateEndpoint,
    TextGenerationIdFeedbackUpdateResponse,
)
from genai.schema._api import (
    _TextGenerationIdFeedbackCreateParametersQuery,
    _TextGenerationIdFeedbackCreateRequest,
    _TextGenerationIdFeedbackRetrieveParametersQuery,
    _TextGenerationIdFeedbackUpdateParametersQuery,
    _TextGenerationIdFeedbackUpdateRequest,
)

T = TypeVar("T", bound=BaseModel)

__all__ = ["FeedbackService"]


class FeedbackService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=TextGenerationIdFeedbackRetrieveEndpoint)
    def retrieve(
        self,
        generation_id: str,
    ) -> TextGenerationIdFeedbackRetrieveResponse:
        """
        Retrieve feedback for the generated output in the given response.

        Raises:
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        metadata = get_service_action_metadata(self.retrieve)
        assert_is_not_empty_string(generation_id)
        self._log_method_execution("Text Generation Feedback Retrieve", generation_id=generation_id)

        with self._get_http_client() as client:
            http_response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=generation_id),
                params=_TextGenerationIdFeedbackRetrieveParametersQuery().model_dump(),
            )
            return TextGenerationIdFeedbackRetrieveResponse(**http_response.json())

    @set_service_action_metadata(endpoint=TextGenerationIdFeedbackCreateEndpoint)
    def create(
        self,
        generation_id: str,
        *,
        categories: Optional[list[EnumLike[TextGenerationFeedbackCategory]]] = None,
        comment: Optional[str] = None,
    ) -> TextGenerationIdFeedbackCreateResponse:
        """
        Provide feedback on generated output for further improvement of the models.

        Args:
            generation_id: A string representing the ID of the text generation.
            categories: An optional list of enum-like objects representing the feedback categories.
            comment: An optional string representing the feedback comment.

        Raises:
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(generation_id)
        self._log_method_execution(
            "Text Generation Feedback Create", generation_id=generation_id, categories=categories, comment=comment
        )

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            http_response = client.post(
                url=self._get_endpoint(metadata.endpoint, id=generation_id),
                params=_TextGenerationIdFeedbackCreateParametersQuery().model_dump(),
                json=_TextGenerationIdFeedbackCreateRequest(
                    comment=comment,
                    categories=(
                        [to_enum(TextGenerationFeedbackCategory, category) for category in categories]
                        if categories is not None
                        else None
                    ),
                ).model_dump(),
            )
            return TextGenerationIdFeedbackCreateResponse(**http_response.json())

    @set_service_action_metadata(endpoint=TextGenerationIdFeedbackUpdateEndpoint)
    def update(
        self,
        generation_id: str,
        categories: Optional[list[TextGenerationFeedbackCategory]] = None,
        comment: Optional[str] = None,
    ) -> TextGenerationIdFeedbackUpdateResponse:
        """
        Update existing feedback.

        Args:
            generation_id: The ID of the text generation to update.
            categories: Optional. List of text generation feedback categories.
            comment: Optional. Comment for the text generation feedback.

        Raises:
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(generation_id)
        self._log_method_execution(
            "Text Generation Feedback Update", generation_id=generation_id, categories=categories, comment=comment
        )

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.update)
            http_response = client.put(
                url=self._get_endpoint(metadata.endpoint, id=generation_id),
                params=_TextGenerationIdFeedbackUpdateParametersQuery().model_dump(),
                json=_TextGenerationIdFeedbackUpdateRequest(comment=comment, categories=categories).model_dump(),
            )
            return TextGenerationIdFeedbackUpdateResponse(**http_response.json())
