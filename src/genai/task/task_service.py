from typing import Optional, TypeVar

from pydantic import BaseModel

from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai.schema import TaskRetrieveEndpoint, TaskRetrieveResponse
from genai.schema._api import _TaskRetrieveParametersQuery

T = TypeVar("T", bound=BaseModel)

__all__ = ["TaskService"]


class TaskService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=TaskRetrieveEndpoint)
    def list(self, *, tune: Optional[bool] = None) -> TaskRetrieveResponse:
        """
        List existing tasks.

        Raises:
            ApiResponseException: In case of an API error.
            ApiNetworkException: In case of unhandled network error.
        """
        request_params = _TaskRetrieveParametersQuery(tune=tune).model_dump()
        self._log_method_execution("Task List", **request_params)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.list)
            http_response = client.get(url=self._get_endpoint(metadata.endpoint), params=request_params)
            return TaskRetrieveResponse(**http_response.json())
