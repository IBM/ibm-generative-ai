from typing import Optional

from genai._generated.api import ModelIdRetrieveParametersQuery
from genai._generated.endpoints import ModelIdRetrieveEndpoint, ModelRetrieveEndpoint
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.model.schema import (
    ModelIdRetrieveResponse,
    ModelRetrieveParametersQuery,
    ModelRetrieveResponse,
)

__all__ = ["ModelService"]


class ModelService(BaseService[BaseServiceConfig, BaseServiceServices]):
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
            response = client.get(
                url=self._get_endpoint(ModelIdRetrieveEndpoint, id=id),
                params=ModelIdRetrieveParametersQuery().model_dump(),
            )
            return ModelIdRetrieveResponse(**response.json())

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
        request_parameters = ModelRetrieveParametersQuery(limit=limit, offset=offset).model_dump()
        self._log_method_execution("Models List", **request_parameters)

        with self._get_http_client() as client:
            response = client.get(url=self._get_endpoint(ModelRetrieveEndpoint), params=request_parameters)
            return ModelRetrieveResponse(**response.json())
