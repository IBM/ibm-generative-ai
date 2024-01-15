from typing import Optional

from genai._generated.api import (
    TuneCreateParametersQuery,
    TuneCreateRequest,
    TuneIdContentTypeRetrieveParametersQuery,
    TuneIdDeleteParametersQuery,
    TuneIdRetrieveParametersQuery,
    TuneRetrieveParametersQuery,
    TuningTypeRetrieveParametersQuery,
)
from genai._generated.endpoints import (
    TuneCreateEndpoint,
    TuneIdContentTypeRetrieveEndpoint,
    TuneIdDeleteEndpoint,
    TuneIdRetrieveEndpoint,
    TuneRetrieveEndpoint,
    TuningTypeRetrieveEndpoint,
)
from genai._types import EnumLike, ModelLike
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai._utils.general import to_enum, to_enum_optional, to_model_optional
from genai._utils.validators import assert_is_not_empty_string
from genai.tune.schema import (
    TuneAssetType,
    TuneCreateResponse,
    TuneIdRetrieveResponse,
    TuneParameters,
    TuneRetrieveResponse,
    TuneStatus,
    TuningType,
    TuningTypeRetrieveResponse,
)

__all__ = ["TuneService"]


class TuneService(BaseService[BaseServiceConfig, BaseServiceServices]):
    def create(
        self,
        *,
        model_id: str,
        name: str,
        task_id: str,
        training_file_ids: list[str],
        tuning_type: EnumLike[TuningType],
        validation_file_ids: Optional[list[str]] = None,
        parameters: Optional[ModelLike[TuneParameters]] = None,
    ) -> TuneCreateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        with self._get_http_client() as client:
            request_body = TuneCreateRequest(
                model_id=model_id,
                name=name,
                parameters=to_model_optional(parameters, TuneParameters),
                task_id=task_id,
                training_file_ids=training_file_ids,
                tuning_type=to_enum(TuningType, tuning_type),
                validation_file_ids=validation_file_ids,
            ).model_dump()

            self._log_method_execution("Tune Create", **request_body)
            response = client.post(
                url=self._get_endpoint(TuneCreateEndpoint),
                params=TuneCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return TuneCreateResponse(**response.json())

    def read(self, *, id: str, type: EnumLike[TuneAssetType]) -> bytes:
        """
        Download tune assets.

        Raises:
            ValueError: if the tune status is not 'COMPLETED'.
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Tune Read", id=id)

        tune = self.retrieve(id).result
        if not tune.status or tune.status != TuneStatus.COMPLETED:
            raise ValueError(
                f"Tune status: '{tune.status.value if tune.status else 'unknown'}'."
                f"Tune can not be downloaded if status is not '{TuneStatus.COMPLETED.value}'."
            )

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(TuneIdContentTypeRetrieveEndpoint, id=id, type=to_enum(TuneAssetType, type)),
                params=TuneIdContentTypeRetrieveParametersQuery().model_dump(),
            )
            return response.content

    def retrieve(
        self,
        id: str,
    ) -> TuneIdRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Tune Retrieve", id=id)

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(TuneIdRetrieveEndpoint, id=id),
                params=TuneIdRetrieveParametersQuery().model_dump(),
            )
            return TuneIdRetrieveResponse(**response.json())

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[TuneStatus] = None,
        search: Optional[str] = None,
    ) -> TuneRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Tune List")

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(TuneRetrieveEndpoint),
                params=TuneRetrieveParametersQuery(
                    limit=limit, offset=offset, status=to_enum_optional(status, TuneStatus), search=search
                ).model_dump(),
            )
            return TuneRetrieveResponse(**response.json())

    def types(self) -> TuningTypeRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(TuningTypeRetrieveEndpoint),
                params=TuningTypeRetrieveParametersQuery().model_dump(),
            )

            self._log_method_execution("Tune Types")
            return TuningTypeRetrieveResponse(**response.json())

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
        self._log_method_execution("Tune Delete")

        with self._get_http_client() as client:
            client.delete(
                url=self._get_endpoint(TuneIdDeleteEndpoint, id=id), params=TuneIdDeleteParametersQuery().model_dump()
            )
