from typing import Optional

from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    TextSentenceSimilarityCreateEndpoint,
    TextSentenceSimilarityCreateResponse,
)
from genai.schema._api import (
    TextSentenceSimilarityParameters,
    _TextSentenceSimilarityCreateParametersQuery,
    _TextSentenceSimilarityCreateRequest,
)

__all__ = ["SentenceSimilarityService"]


class SentenceSimilarityService(BaseService[BaseServiceConfig, BaseServiceServices]):
    """
    EXPERIMENTAL Text Sentence Similarity service, this service may change in the near future.
    """

    @set_service_action_metadata(endpoint=TextSentenceSimilarityCreateEndpoint)
    def create(
        self,
        *,
        model_id: str,
        source_sentence: str,
        sentences: list[str],
        parameters: Optional[TextSentenceSimilarityParameters] = None,
    ) -> TextSentenceSimilarityCreateResponse:
        request_body = _TextSentenceSimilarityCreateRequest(
            model_id=model_id, source_sentence=source_sentence, sentences=sentences, parameters=parameters
        ).model_dump()

        self._log_method_execution("Sentence Similarity Create", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            http_response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextSentenceSimilarityCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return TextSentenceSimilarityCreateResponse(**http_response.json())
