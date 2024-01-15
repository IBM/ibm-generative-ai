from genai._generated.api import TextEmbeddingLimitRetrieveParametersQuery
from genai._generated.endpoints import TextEmbeddingLimitRetrieveEndpoint
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai.text.embedding.limit.schema import TextEmbeddingLimitRetrieveResponse

__all__ = ["LimitService"]


class LimitService(BaseService[BaseServiceConfig, BaseServiceServices]):
    def retrieve(self) -> TextEmbeddingLimitRetrieveResponse:
        """
        Retrieves the current text embedding limit from the server.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Limit Retrieve")

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(TextEmbeddingLimitRetrieveEndpoint),
                params=TextEmbeddingLimitRetrieveParametersQuery().model_dump(),
            )
            return TextEmbeddingLimitRetrieveResponse(**response.json())

    async def aretrieve(self) -> TextEmbeddingLimitRetrieveResponse:
        """
        Retrieves the current text embedding limit from the server.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Limit ARetrieve")

        async with self._get_async_http_client() as client:
            response = await client.get(
                url=self._get_endpoint(TextEmbeddingLimitRetrieveEndpoint),
                params=TextEmbeddingLimitRetrieveParametersQuery().model_dump(),
            )
            return TextEmbeddingLimitRetrieveResponse(**response.json())
