from typing import Optional, Union

from genai._generated.api import (
    PromptCreateParametersQuery,
    PromptCreateRequest,
    PromptIdDeleteParametersQuery,
    PromptIdRetrieveParametersQuery,
    PromptIdUpdateParametersQuery,
    PromptIdUpdateRequest,
    PromptRetrieveParametersQuery,
    PromptTemplateData,
)
from genai._generated.endpoints import (
    PromptCreateEndpoint,
    PromptIdDeleteEndpoint,
    PromptIdRetrieveEndpoint,
    PromptIdUpdateEndpoint,
    PromptRetrieveEndpoint,
)
from genai._types import EnumLike, EnumLikeOrEnumLikeList, ModelLike
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai._utils.general import (
    cast_list,
    to_enum,
    to_enum_optional,
    to_model_instance,
    to_model_optional,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.prompt.schema import (
    BaseMessage,
    ModerationParameters,
    PromptCreateResponse,
    PromptIdRetrieveResponse,
    PromptIdUpdateResponse,
    PromptRetrieveRequestParamsSource,
    PromptRetrieveResponse,
    PromptType,
    TextGenerationParameters,
)

__all__ = ["PromptService"]


class PromptService(BaseService[BaseServiceConfig, BaseServiceServices]):
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
    ) -> PromptCreateResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_body = PromptCreateRequest(
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
        ).model_dump()

        self._log_method_execution("Prompts Create", **request_body)

        with self._get_http_client() as client:
            response = client.post(
                url=self._get_endpoint(PromptCreateEndpoint),
                params=PromptCreateParametersQuery().model_dump(),
                json=request_body,
            )
            return PromptCreateResponse(**response.json())

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
            response = client.get(
                url=self._get_endpoint(PromptIdRetrieveEndpoint, id=id),
                params=PromptIdRetrieveParametersQuery().model_dump(),
            )
            return PromptIdRetrieveResponse(**response.json())

    def update(
        self,
        id: str,
        *,
        name: str,
        model_id: str,
        description: Optional[str] = None,
        input: Optional[str] = None,
        output: Optional[str],
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
        request_body = PromptIdUpdateRequest(
            name=name,
            model_id=model_id,
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

        self._log_method_execution("Prompts Update", **request_body)

        with self._get_http_client() as client:
            response = client.post(
                url=self._get_endpoint(PromptIdUpdateEndpoint, id=id),
                params=PromptIdUpdateParametersQuery().model_dump(),
                json=request_body,
            )
            return PromptIdUpdateResponse(**response.json())

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        task_id: Optional[Union[str, list[str]]] = None,
        model_id: Optional[Union[str, list[str]]] = None,
        source: Optional[EnumLikeOrEnumLikeList[PromptRetrieveRequestParamsSource]] = None,
    ) -> PromptRetrieveResponse:
        """
        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_parameters = PromptRetrieveParametersQuery(
            limit=limit,
            offset=offset,
            search=search,
            task_id=task_id,
            model_id=model_id,
            source=[to_enum(PromptRetrieveRequestParamsSource, s) for s in cast_list(source)] if source else None,
        ).model_dump()
        self._log_method_execution("Prompts List", **request_parameters)

        with self._get_http_client() as client:
            response = client.get(url=self._get_endpoint(PromptRetrieveEndpoint), params=request_parameters)
            return PromptRetrieveResponse(**response.json())

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
        self._log_method_execution("Prompts Delete", id=id)

        with self._get_http_client() as client:
            client.delete(
                url=self._get_endpoint(PromptIdDeleteEndpoint, id=id),
                params=PromptIdDeleteParametersQuery().model_dump(),
            )
