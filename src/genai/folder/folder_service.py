from typing import Optional, TypeVar

from pydantic import BaseModel

from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import (
    FolderCreateEndpoint,
    FolderIdDeleteEndpoint,
    FolderIdRetrieveEndpoint,
    FolderRetrieveEndpoint,
    FolderRetrieveResponse,
)
from genai.schema._api import (
    FolderCreateResponse,
    FolderIdRetrieveResponse,
    _FolderCreateParametersQuery,
    _FolderCreateRequest,
    _FolderIdDeleteParametersQuery,
    _FolderIdRetrieveParametersQuery,
    _FolderRetrieveParametersQuery,
)

T = TypeVar("T", bound=BaseModel)

__all__ = ["FolderService"]


class FolderService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=FolderRetrieveEndpoint)
    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> FolderRetrieveResponse:
        """
        List existing folders.

        Raises:
            ApiResponseException: In case of an API error.
            ApiNetworkException: In case of unhandled network error.
        """
        request_params = _FolderRetrieveParametersQuery(limit=limit, offset=offset).model_dump()
        self._log_method_execution("Folder List", **request_params)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.list)
            http_response = client.get(url=self._get_endpoint(metadata.endpoint), params=request_params)
            return FolderRetrieveResponse(**http_response.json())

    @set_service_action_metadata(endpoint=FolderCreateEndpoint)
    def create(self, name: str) -> FolderCreateResponse:
        """
        Args:
            name: The name of the folder to be created.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        request_body = _FolderCreateRequest(name=name).model_dump()
        self._log_method_execution("Folder Create", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_FolderCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return FolderCreateResponse(**response.json())

    @set_service_action_metadata(endpoint=FolderIdRetrieveEndpoint)
    def retrieve(
        self,
        id: str,
    ) -> FolderIdRetrieveResponse:
        """
        Args:
            id: The ID of the folder to retrieve.

        Raises:
            ValueError: If the provided ID is an empty string.
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Folder Retrieve", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.retrieve)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_FolderIdRetrieveParametersQuery().model_dump(),
            )
            return FolderIdRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=FolderIdDeleteEndpoint)
    def delete(self, id: str) -> None:
        """
        Deletes a folder with the given ID.

        Args:
            id: The ID of the folder to be deleted.

        Raises:
            ValueError: If the ID is an empty string.
            ApiResponseException: In case of a known API error (ex: file does not exist).
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Folder Delete", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.delete)
            client.delete(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_FolderIdDeleteParametersQuery().model_dump(),
            )
