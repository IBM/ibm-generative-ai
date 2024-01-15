from typing import Optional

from genai._generated.api import (
    UserCreateParametersQuery,
    UserCreateRequest,
    UserDeleteParametersQuery,
    UserPatchParametersQuery,
    UserPatchRequest,
    UserRetrieveParametersQuery,
)
from genai._generated.endpoints import (
    UserCreateEndpoint,
    UserDeleteEndpoint,
    UserPatchEndpoint,
    UserRetrieveEndpoint,
)
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai.user.schema import (
    UserCreateResponse,
    UserPatchResponse,
    UserRetrieveResponse,
)

__all__ = ["UserService"]


class UserService(BaseService[BaseServiceConfig, BaseServiceServices]):
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
        request_body = UserCreateRequest(first_name=first_name, last_name=last_name).model_dump()
        self._log_method_execution("User Create", **request_body)

        with self._get_http_client() as client:
            response = client.post(
                url=self._get_endpoint(UserCreateEndpoint),
                json=request_body,
                params=UserCreateParametersQuery().model_dump(),
            )
            return UserCreateResponse(**response.json())

    def retrieve(self) -> UserRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("User Retrieve")

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(UserRetrieveEndpoint), params=UserRetrieveParametersQuery().model_dump()
            )
            return UserRetrieveResponse(**response.json())

    def update(self, *, tou_accepted: Optional[bool] = None) -> UserPatchResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        request_body = UserPatchRequest(tou_accepted=tou_accepted).model_dump()
        self._log_method_execution("User Update", **request_body)

        with self._get_http_client() as client:
            response = client.patch(
                url=self._get_endpoint(UserPatchEndpoint),
                json=request_body,
                params=UserPatchParametersQuery().model_dump(),
            )
            return UserPatchResponse(**response.json())

    def delete(self) -> None:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("User Delete")

        with self._get_http_client() as client:
            client.delete(url=self._get_endpoint(UserDeleteEndpoint), params=UserDeleteParametersQuery().model_dump())
