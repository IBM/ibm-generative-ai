from typing import Optional, TypeVar

from pydantic import BaseModel

from genai._generated.api import (
    TextGenerationIdFeedbackCreateParametersQuery,
    TextGenerationIdFeedbackCreateRequest,
    TextGenerationIdFeedbackRetrieveParametersQuery,
    TextGenerationIdFeedbackUpdateParametersQuery,
    TextGenerationIdFeedbackUpdateRequest,
)
from genai._generated.endpoints import (
    TextGenerationIdFeedbackCreateEndpoint,
    TextGenerationIdFeedbackRetrieveEndpoint,
    TextGenerationIdFeedbackUpdateEndpoint,
)
from genai._types import EnumLike
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai._utils.general import to_enum
from genai._utils.validators import assert_is_not_empty_string
from genai.text.generation.feedback.schema import (
    TextGenerationFeedbackCategory,
    TextGenerationIdFeedbackCreateResponse,
    TextGenerationIdFeedbackRetrieveResponse,
    TextGenerationIdFeedbackUpdateResponse,
)

T = TypeVar("T", bound=BaseModel)

__all__ = ["FeedbackService"]


class FeedbackService(BaseService[BaseServiceConfig, BaseServiceServices]):
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
        assert_is_not_empty_string(generation_id)
        self._log_method_execution("Text Generation Feedback Retrieve", generation_id=generation_id)

        with self._get_http_client() as client:
            http_response = client.get(
                url=self._get_endpoint(TextGenerationIdFeedbackRetrieveEndpoint, id=generation_id),
                params=TextGenerationIdFeedbackRetrieveParametersQuery().model_dump(),
            )
            return TextGenerationIdFeedbackRetrieveResponse(**http_response.json())

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
            http_response = client.post(
                url=self._get_endpoint(TextGenerationIdFeedbackCreateEndpoint, id=generation_id),
                params=TextGenerationIdFeedbackCreateParametersQuery().model_dump(),
                json=TextGenerationIdFeedbackCreateRequest(
                    comment=comment,
                    categories=(
                        [to_enum(TextGenerationFeedbackCategory, category) for category in categories]
                        if categories is not None
                        else None
                    ),
                ).model_dump(),
            )
            return TextGenerationIdFeedbackCreateResponse(**http_response.json())

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
            http_response = client.put(
                url=self._get_endpoint(TextGenerationIdFeedbackUpdateEndpoint, id=generation_id),
                params=TextGenerationIdFeedbackUpdateParametersQuery().model_dump(),
                json=TextGenerationIdFeedbackUpdateRequest(comment=comment, categories=categories).model_dump(),
            )
            return TextGenerationIdFeedbackUpdateResponse(**http_response.json())
