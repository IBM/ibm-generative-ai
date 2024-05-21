from typing import Optional

from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import (
    DeploymentCreateEndpoint,
    DeploymentIdDeleteEndpoint,
    DeploymentIdRetrieveEndpoint,
    DeploymentRetrieveEndpoint,
)
from genai.schema._api import (
    DeploymentCreateResponse,
    DeploymentIdRetrieveResponse,
    DeploymentRetrieveResponse,
    _DeploymentCreateParametersQuery,
    _DeploymentCreateRequest,
    _DeploymentIdDeleteParametersQuery,
    _DeploymentIdRetrieveParametersQuery,
    _DeploymentRetrieveParametersQuery,
)

__all__ = ["DeploymentService"]


class DeploymentService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=DeploymentCreateEndpoint)
    def create(
        self,
        *,
        tune_id: str,
    ) -> DeploymentCreateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            request_body = _DeploymentCreateRequest(tune_id=tune_id).model_dump()

            self._log_method_execution("Deployment Create", **request_body)
            response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_DeploymentCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return DeploymentCreateResponse(**response.json())

    @set_service_action_metadata(endpoint=DeploymentIdRetrieveEndpoint)
    def retrieve(
        self,
        id: str,
    ) -> DeploymentIdRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        metadata = get_service_action_metadata(self.retrieve)
        assert_is_not_empty_string(id)
        self._log_method_execution("Deployment Retrieve", id=id)

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_DeploymentIdRetrieveParametersQuery().model_dump(),
            )
            return DeploymentIdRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=DeploymentRetrieveEndpoint)
    def list(
        self,
        *,
        id: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> DeploymentRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Deployment Retrieve")
        metadata = get_service_action_metadata(self.list)

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(metadata.endpoint),
                params=_DeploymentRetrieveParametersQuery(id=id, limit=limit, offset=offset).model_dump(),
            )
            return DeploymentRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=DeploymentIdDeleteEndpoint)
    def delete(
        self,
        id: str,
    ) -> None:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Deployment Delete", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.delete)
            client.delete(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_DeploymentIdDeleteParametersQuery().model_dump(),
            )
