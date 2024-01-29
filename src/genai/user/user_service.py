from typing import Optional

from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    UserCreateEndpoint,
    UserCreateResponse,
    UserDeleteEndpoint,
    UserPatchEndpoint,
    UserPatchResponse,
    UserRetrieveEndpoint,
    UserRetrieveResponse,
)
from genai.schema._api import (
    _UserCreateParametersQuery,
    _UserCreateRequest,
    _UserDeleteParametersQuery,
    _UserPatchParametersQuery,
    _UserPatchRequest,
    _UserRetrieveParametersQuery,
)

__all__ = ["UserService"]


class UserService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=UserCreateEndpoint)
    def create(
        self,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> UserCreateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        request_body = _UserCreateRequest(first_name=first_name, last_name=last_name).model_dump()
        self._log_method_execution("User Create", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                json=request_body,
                params=_UserCreateParametersQuery().model_dump(),
            )
            return UserCreateResponse(**response.json())

    @set_service_action_metadata(endpoint=UserRetrieveEndpoint)
    def retrieve(self) -> UserRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("User Retrieve")

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.retrieve)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint), params=_UserRetrieveParametersQuery().model_dump()
            )
            return UserRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=UserPatchEndpoint)
    def update(self, *, tou_accepted: Optional[bool] = None) -> UserPatchResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        request_body = _UserPatchRequest(tou_accepted=tou_accepted).model_dump()
        self._log_method_execution("User Update", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.update)
            response = client.patch(
                url=self._get_endpoint(metadata.endpoint),
                json=request_body,
                params=_UserPatchParametersQuery().model_dump(),
            )
            return UserPatchResponse(**response.json())

    @set_service_action_metadata(endpoint=UserDeleteEndpoint)
    def delete(self) -> None:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("User Delete")

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.delete)
            client.delete(url=self._get_endpoint(metadata.endpoint), params=_UserDeleteParametersQuery().model_dump())
