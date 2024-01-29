from typing import Optional

from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    SystemPromptCreateEndpoint,
    SystemPromptCreateResponse,
    SystemPromptIdDeleteEndpoint,
    SystemPromptIdRetrieveEndpoint,
    SystemPromptIdRetrieveResponse,
    SystemPromptIdUpdateEndpoint,
    SystemPromptIdUpdateResponse,
    SystemPromptRetrieveEndpoint,
    SystemPromptRetrieveResponse,
)
from genai.schema._api import (
    _SystemPromptCreateParametersQuery,
    _SystemPromptCreateRequest,
    _SystemPromptIdDeleteParametersQuery,
    _SystemPromptIdRetrieveParametersQuery,
    _SystemPromptIdUpdateParametersQuery,
    _SystemPromptIdUpdateRequest,
    _SystemPromptRetrieveParametersQuery,
)

__all__ = ["SystemPromptService"]


class SystemPromptService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=SystemPromptCreateEndpoint)
    def create(self, *, name: str, content: str) -> SystemPromptCreateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_body = _SystemPromptCreateRequest(name=name, content=content).model_dump()

        self._log_method_execution("System Prompt Create", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_SystemPromptCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return SystemPromptCreateResponse(**response.json())

    @set_service_action_metadata(endpoint=SystemPromptIdRetrieveEndpoint)
    def retrieve(
        self,
        id: int,
    ) -> SystemPromptIdRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        self._log_method_execution("System Prompt Retrieve", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.retrieve)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_SystemPromptIdRetrieveParametersQuery().model_dump(),
            )
            return SystemPromptIdRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=SystemPromptIdUpdateEndpoint)
    def update(self, id: int, *, name: str, content: str) -> SystemPromptIdUpdateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_body = _SystemPromptIdUpdateRequest(name=name, content=content).model_dump()

        self._log_method_execution("System Prompt Update", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.update)
            response = client.post(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_SystemPromptIdUpdateParametersQuery().model_dump(),
                json=request_body,
            )
            return SystemPromptIdUpdateResponse(**response.json())

    @set_service_action_metadata(endpoint=SystemPromptRetrieveEndpoint)
    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> SystemPromptRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_parameters = _SystemPromptRetrieveParametersQuery(
            limit=limit,
            offset=offset,
        ).model_dump()
        self._log_method_execution("System Prompt List", **request_parameters)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.list)
            response = client.get(url=self._get_endpoint(metadata.endpoint), params=request_parameters)
            return SystemPromptRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=SystemPromptIdDeleteEndpoint)
    def delete(
        self,
        id: int,
    ) -> None:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        self._log_method_execution("System Prompt Delete", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.delete)
            client.delete(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_SystemPromptIdDeleteParametersQuery().model_dump(),
            )
