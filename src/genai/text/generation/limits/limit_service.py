from genai._generated.api import TextGenerationLimitRetrieveParametersQuery
from genai._generated.endpoints import TextGenerationLimitRetrieveEndpoint
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai.text.generation.limits.schema import TextGenerationLimitRetrieveResponse

__all__ = ["LimitService"]


class LimitService(BaseService[BaseServiceConfig, BaseServiceServices]):
    def retrieve(self) -> TextGenerationLimitRetrieveResponse:
        """
        Retrieves the current text generation limit from the server.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Text Generation Limit Retrieve")

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(TextGenerationLimitRetrieveEndpoint),
                params=TextGenerationLimitRetrieveParametersQuery().model_dump(),
            )
            return TextGenerationLimitRetrieveResponse(**response.json())

    async def aretrieve(self) -> TextGenerationLimitRetrieveResponse:
        """
        Retrieves the current text generation limit from the server.

        Raises:
            ApiResponseException: If target feedback/generation does not exist or cannot be updated.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Text Generation Limit ARetrieve")

        async with self._get_async_http_client() as client:
            response = await client.get(
                url=self._get_endpoint(TextGenerationLimitRetrieveEndpoint),
                params=TextGenerationLimitRetrieveParametersQuery().model_dump(),
            )
            return TextGenerationLimitRetrieveResponse(**response.json())
