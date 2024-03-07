from typing import Optional, TypeVar

from pydantic import BaseModel

from genai._types import EnumLike
from genai._utils.general import to_enum_optional
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import (
    TagRetrieveEndpoint,
    TagRetrieveResponse,
    TagType,
)
from genai.schema._api import _TagRetrieveParametersQuery

T = TypeVar("T", bound=BaseModel)

__all__ = ["TagService"]


class TagService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=TagRetrieveEndpoint)
    def list(
        self, *, limit: Optional[int] = None, offset: Optional[int] = None, type: Optional[EnumLike[TagType]] = None
    ) -> TagRetrieveResponse:
        """
        List existing tags.

        Raises:
            ApiResponseException: In case of an API error.
            ApiNetworkException: In case of unhandled network error.
        """
        request_params = _TagRetrieveParametersQuery(
            limit=limit,
            offset=offset,
            type=to_enum_optional(type, TagType),
        ).model_dump()
        self._log_method_execution("Tag List", **request_params)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.list)
            http_response = client.get(url=self._get_endpoint(metadata.endpoint), params=request_params)
            return TagRetrieveResponse(**http_response.json())
