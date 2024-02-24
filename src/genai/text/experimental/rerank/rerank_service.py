from typing import Optional

from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    TextRerankCreateEndpoint,
    TextRerankCreateResponse,
)
from genai.schema._api import (
    TextRerankParameters,
    _TextRerankCreateParametersQuery,
    _TextRerankCreateRequest,
)

__all__ = ["RerankService"]


class RerankService(BaseService[BaseServiceConfig, BaseServiceServices]):
    """
    EXPERIMENTAL Text rerank service, this service may change in the near future.
    """

    @set_service_action_metadata(endpoint=TextRerankCreateEndpoint)
    def create(
        self, *, model_id: str, query: str, documents: list[str], parameters: Optional[TextRerankParameters] = None
    ) -> TextRerankCreateResponse:
        request_body = _TextRerankCreateRequest(
            model_id=model_id, documents=documents, parameters=parameters, query=query
        ).model_dump()

        self._log_method_execution("Rerank Create", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            http_response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextRerankCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return TextRerankCreateResponse(**http_response.json())
