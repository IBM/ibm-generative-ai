from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import TextGenerationLimitRetrieveEndpoint, TextGenerationLimitRetrieveResponse
from genai.schema._api import _TextGenerationLimitRetrieveParametersQuery

__all__ = ["LimitService"]


class LimitService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=TextGenerationLimitRetrieveEndpoint)
    def retrieve(self) -> TextGenerationLimitRetrieveResponse:
        """
        Retrieves the current text generation limit from the server.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Text Generation Limit Retrieve")

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.retrieve)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextGenerationLimitRetrieveParametersQuery().model_dump(),
            )
            return TextGenerationLimitRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=TextGenerationLimitRetrieveEndpoint)
    async def aretrieve(self) -> TextGenerationLimitRetrieveResponse:
        """
        Retrieves the current text generation limit from the server.

        Raises:
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Text Generation Limit ARetrieve")

        async with self._get_async_http_client() as client:
            metadata = get_service_action_metadata(self.aretrieve)
            response = await client.get(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextGenerationLimitRetrieveParametersQuery().model_dump(),
            )
            return TextGenerationLimitRetrieveResponse(**response.json())
