from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import TextEmbeddingLimitRetrieveEndpoint, TextEmbeddingLimitRetrieveResponse
from genai.schema._api import _TextEmbeddingLimitRetrieveParametersQuery

__all__ = ["LimitService"]


class LimitService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=TextEmbeddingLimitRetrieveEndpoint)
    def retrieve(self) -> TextEmbeddingLimitRetrieveResponse:
        """
        Retrieves the current text embedding limit from the server.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Limit Retrieve")
        metadata = get_service_action_metadata(self.retrieve)

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextEmbeddingLimitRetrieveParametersQuery().model_dump(),
            )
            return TextEmbeddingLimitRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=TextEmbeddingLimitRetrieveEndpoint)
    async def aretrieve(self) -> TextEmbeddingLimitRetrieveResponse:
        """
        Retrieves the current text embedding limit from the server.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        self._log_method_execution("Limit ARetrieve")
        metadata = get_service_action_metadata(self.aretrieve)

        async with self._get_async_http_client() as client:
            response = await client.get(
                url=self._get_endpoint(metadata.endpoint),
                params=_TextEmbeddingLimitRetrieveParametersQuery().model_dump(),
            )
            return TextEmbeddingLimitRetrieveResponse(**response.json())
