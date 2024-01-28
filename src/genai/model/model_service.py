from typing import Optional

from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import ModelIdRetrieveResponse, ModelRetrieveResponse
from genai.schema._api import _ModelIdRetrieveParametersQuery, _ModelRetrieveParametersQuery
from genai.schema._endpoints import ModelIdRetrieveEndpoint, ModelRetrieveEndpoint

__all__ = ["ModelService"]


class ModelService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=ModelIdRetrieveEndpoint)
    def retrieve(
        self,
        id: str,
    ) -> ModelIdRetrieveResponse:
        """
        Raises:
            ValueError: If the id parameter is an empty string.
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Models Retrieve", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.retrieve)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_ModelIdRetrieveParametersQuery().model_dump(),
            )
            return ModelIdRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=ModelRetrieveEndpoint)
    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> ModelRetrieveResponse:
        """
        Args:
            limit: The maximum number of models to retrieve.
            offset: The number of models to skip before starting to retrieve.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_parameters = _ModelRetrieveParametersQuery(limit=limit, offset=offset).model_dump()
        self._log_method_execution("Models List", **request_parameters)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.list)
            response = client.get(url=self._get_endpoint(metadata.endpoint), params=request_parameters)
            return ModelRetrieveResponse(**response.json())
