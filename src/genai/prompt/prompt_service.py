from typing import Optional, Union

from genai._types import EnumLike, EnumLikeOrEnumLikeList, ModelLike
from genai._utils.general import (
    cast_list,
    cast_list_optional,
    to_enum,
    to_enum_optional,
    to_model_instance,
    to_model_optional,
)
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import (
    BaseMessage,
    ModerationParameters,
    PromptCreateResponse,
    PromptIdRetrieveResponse,
    PromptIdUpdateResponse,
    PromptListSource,
    PromptRetrieveResponse,
    PromptTemplateData,
    PromptType,
    TextGenerationParameters,
)
from genai.schema._api import (
    PromptListSortBy,
    SortDirection,
    _PromptCreateParametersQuery,
    _PromptCreateRequest,
    _PromptIdDeleteParametersQuery,
    _PromptIdRetrieveParametersQuery,
    _PromptIdUpdateParametersQuery,
    _PromptIdUpdateRequest,
    _PromptRetrieveParametersQuery,
)
from genai.schema._endpoints import (
    PromptCreateEndpoint,
    PromptIdDeleteEndpoint,
    PromptIdRetrieveEndpoint,
    PromptIdUpdateEndpoint,
    PromptRetrieveEndpoint,
)

__all__ = ["PromptService"]


class PromptService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=PromptCreateEndpoint)
    def create(
        self,
        *,
        name: str,
        model_id: str,
        prompt_id: Optional[str] = None,
        messages: Optional[list[ModelLike[BaseMessage]]] = None,
        task_id: Optional[str] = None,
        description: Optional[str] = None,
        moderations: Optional[ModelLike[ModerationParameters]] = None,
        data: Optional[ModelLike[PromptTemplateData]] = None,
        type: Optional[EnumLike[PromptType]] = None,
        input: Optional[str] = None,
        output: Optional[str] = None,
        parameters: Optional[ModelLike[TextGenerationParameters]] = None,
        folder_id: Optional[str] = None,
    ) -> PromptCreateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_body = _PromptCreateRequest(
            name=name,
            model_id=model_id,
            prompt_id=prompt_id,
            messages=[to_model_instance(msg, BaseMessage) for msg in messages] if messages else None,
            task_id=task_id,
            description=description,
            moderations=to_model_optional(moderations, ModerationParameters),
            data=to_model_optional(data, PromptTemplateData),
            input=input,
            output=output,
            parameters=to_model_optional(parameters, TextGenerationParameters),
            type=to_enum_optional(type, PromptType),
            folder_id=folder_id,
        ).model_dump()

        self._log_method_execution("Prompt Create", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.create)
            response = client.post(
                url=self._get_endpoint(metadata.endpoint),
                params=_PromptCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return PromptCreateResponse(**response.json())

    @set_service_action_metadata(endpoint=PromptIdRetrieveEndpoint)
    def retrieve(
        self,
        id: str,
    ) -> PromptIdRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Prompts Retrieve", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.retrieve)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_PromptIdRetrieveParametersQuery().model_dump(),
            )
            return PromptIdRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=PromptIdUpdateEndpoint)
    def update(
        self,
        id: str,
        *,
        name: str,
        model_id: str,
        folder_id: Optional[str] = None,
        industry_id: Optional[str] = None,
        language_id: Optional[str] = None,
        description: Optional[str] = None,
        input: Optional[str] = None,
        output: Optional[str] = None,
        task_id: Optional[str] = None,
        type: Optional[EnumLike[PromptType]] = None,
        messages: Optional[list[ModelLike[BaseMessage]]] = None,
        moderations: Optional[ModelLike[ModerationParameters]] = None,
        parameters: Optional[ModelLike[TextGenerationParameters]] = None,
        data: Optional[ModelLike[PromptTemplateData]] = None,
    ) -> PromptIdUpdateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        assert_is_not_empty_string(id)
        request_body = _PromptIdUpdateRequest(
            name=name,
            model_id=model_id,
            folder_id=folder_id,
            industry_id=industry_id,
            language_id=language_id,
            messages=[to_model_instance(msg, BaseMessage) for msg in messages] if messages else None,
            task_id=task_id,
            description=description,
            moderations=to_model_optional(moderations, ModerationParameters),
            data=to_model_optional(data, PromptTemplateData),
            input=input,
            output=output,
            parameters=to_model_optional(parameters, TextGenerationParameters),
            type=to_enum_optional(type, PromptType),
        ).model_dump()

        self._log_method_execution("Prompt Update", **request_body)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.update)
            response = client.post(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_PromptIdUpdateParametersQuery().model_dump(),
                json=request_body,
            )
            return PromptIdUpdateResponse(**response.json())

    @set_service_action_metadata(endpoint=PromptRetrieveEndpoint)
    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[EnumLike[PromptListSortBy]] = None,
        direction: Optional[EnumLike[SortDirection]] = None,
        search: Optional[str] = None,
        task_id: Optional[Union[str, list[str]]] = None,
        model_id: Optional[Union[str, list[str]]] = None,
        source: Optional[EnumLikeOrEnumLikeList[PromptListSource]] = None,
        model_family_id: Optional[float] = None,
        industry_id: Optional[Union[str, list[str]]] = None,
        prompt_language_id: Optional[Union[str, list[str]]] = None,
        model_type_id: Optional[Union[str, list[str]]] = None,
        avg_time_min: Optional[int] = None,
        avg_time_max: Optional[int] = None,
        context_window_min: Optional[int] = None,
        context_window_max: Optional[int] = None,
        folder_id: Optional[str] = None,
    ) -> PromptRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_parameters = _PromptRetrieveParametersQuery(
            limit=limit,
            offset=offset,
            sort_by=to_enum_optional(sort_by, PromptListSortBy),
            direction=to_enum_optional(direction, SortDirection),
            search=search,
            task_id=cast_list_optional(task_id),
            model_id=cast_list_optional(model_id),
            source=[to_enum(PromptListSource, s) for s in cast_list(source)] if source else None,
            model_family_id=model_family_id,
            industry_id=cast_list_optional(industry_id),
            prompt_language_id=cast_list_optional(prompt_language_id),
            model_type_id=cast_list_optional(model_type_id),
            avg_time_min=avg_time_min,
            avg_time_max=avg_time_max,
            context_window_min=context_window_min,
            context_window_max=context_window_max,
            folder_id=folder_id,
        ).model_dump()
        self._log_method_execution("Prompt List", **request_parameters)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.list)
            response = client.get(url=self._get_endpoint(metadata.endpoint), params=request_parameters)
            return PromptRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=PromptIdDeleteEndpoint)
    def delete(
        self,
        id: str,
    ) -> None:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("Prompt Delete", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.delete)
            client.delete(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_PromptIdDeleteParametersQuery().model_dump(),
            )
