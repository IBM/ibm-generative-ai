from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    TextClassificationCreateEndpoint,
    TextClassificationCreateResponse,
)
from genai.schema._api import (
    TextClassificationCreateData,
    _TextClassificationCreateParametersQuery,
    _TextClassificationCreateRequest,
)

__all__ = ["ClassificationService"]


class ClassificationService(BaseService[BaseServiceConfig, BaseServiceServices]):
    """
    EXPERIMENTAL Text classification service, this service may change in the near future.
    """

    @set_service_action_metadata(endpoint=TextClassificationCreateEndpoint)
    def create(
        self, *, model_id: str, input: str, data: list[TextClassificationCreateData]
    ) -> TextClassificationCreateResponse:
        request_body = _TextClassificationCreateRequest(data=data, input=input, model_id=model_id).model_dump()

        self._log_method_execution("Classification Create", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            http_response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextClassificationCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return TextClassificationCreateResponse(**http_response.json())
