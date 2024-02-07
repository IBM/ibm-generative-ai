from typing import Optional

from genai._types import EnumLike, ModelLike
from genai._utils.general import to_enum, to_enum_optional, to_model_optional
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import (
    TuneAssetType,
    TuneCreateEndpoint,
    TuneCreateResponse,
    TuneIdContentTypeRetrieveEndpoint,
    TuneIdDeleteEndpoint,
    TuneIdRetrieveEndpoint,
    TuneIdRetrieveResponse,
    TuneParameters,
    TuneRetrieveEndpoint,
    TuneRetrieveResponse,
    TuneStatus,
    TuningType,
    TuningTypeRetrieveEndpoint,
    TuningTypeRetrieveResponse,
)
from genai.schema._api import (
    _TuneCreateParametersQuery,
    _TuneCreateRequest,
    _TuneIdContentTypeRetrieveParametersQuery,
    _TuneIdDeleteParametersQuery,
    _TuneIdRetrieveParametersQuery,
    _TuneRetrieveParametersQuery,
    _TuningTypeRetrieveParametersQuery,
)

__all__ = ["TuneService"]


class TuneService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=TuneCreateEndpoint)
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
            metadata = get_service_action_metadata(self.create)
            request_body = _TuneCreateRequest(
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
                url=self._get_endpoint(metadata.endpoint),
                params=_TuneCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return TuneCreateResponse(**response.json())

    @set_service_action_metadata(endpoint=TuneIdContentTypeRetrieveEndpoint)
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

        metadata = get_service_action_metadata(self.read)
        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id, type=to_enum(TuneAssetType, type)),
                params=_TuneIdContentTypeRetrieveParametersQuery().model_dump(),
            )
            return response.content

    @set_service_action_metadata(endpoint=TuneIdRetrieveEndpoint)
    def retrieve(
        self,
        id: str,
    ) -> TuneIdRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        metadata = get_service_action_metadata(self.retrieve)
        assert_is_not_empty_string(id)
        self._log_method_execution("Tune Retrieve", id=id)

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_TuneIdRetrieveParametersQuery().model_dump(),
            )
            return TuneIdRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=TuneRetrieveEndpoint)
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
            metadata = get_service_action_metadata(self.list)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint),
                params=_TuneRetrieveParametersQuery(
                    limit=limit, offset=offset, status=to_enum_optional(status, TuneStatus), search=search
                ).model_dump(),
            )
            return TuneRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=TuningTypeRetrieveEndpoint)
    def types(self) -> TuningTypeRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.types)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint),
                params=_TuningTypeRetrieveParametersQuery().model_dump(),
            )

            self._log_method_execution("Tune Types")
            return TuningTypeRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=TuneIdDeleteEndpoint)
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
            metadata = get_service_action_metadata(self.delete)
            client.delete(
                url=self._get_endpoint(metadata.endpoint, id=id), params=_TuneIdDeleteParametersQuery().model_dump()
            )
