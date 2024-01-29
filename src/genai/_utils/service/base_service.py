from __future__ import annotations

import logging
import re
from abc import ABC
from enum import Enum
from typing import Generic, Optional, TypeVar, Union, cast
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict

from genai._utils.api_client import ApiClient
from genai._utils.general import to_model_instance
from genai._utils.http_client.httpx_client import AsyncHttpxClient, HttpxClient
from genai._utils.service.metadata import inherit_metadata
from genai._utils.shared_options import CommonExecutionOptions
from genai._utils.validators import assert_is_not_empty_string
from genai.schema._endpoints import ApiEndpoint

__all__ = ["BaseService", "BaseServiceConfig", "BaseServiceServices", "CommonExecutionOptions"]


class BaseServiceConfig(BaseModel):
    """Options which given service uses"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True)


class BaseServiceServices(BaseModel):
    """List of services which given service uses"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True)


TConfig = TypeVar("TConfig", bound=BaseServiceConfig)
TServices = TypeVar("TServices", bound=BaseServiceServices)

TClient = TypeVar("TClient", HttpxClient, AsyncHttpxClient)


class BaseService(Generic[TConfig, TServices], ABC):
    """
    A base class for services that interact with an API.

    Attributes:
        Config (type): The type of the configuration class used by the service.
        Services (type): The type of the services class used by the service.
    """

    Config: type[TConfig] = cast(type[TConfig], BaseServiceConfig)
    Services: type[TServices] = cast(type[TServices], BaseServiceServices)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for name in dir(cls):
            method = getattr(cls, name, None)
            if not callable(method) or name.startswith("__"):
                continue

            for base_cls in cls.__bases__:
                if not issubclass(base_cls, BaseService):
                    continue

                target = getattr(base_cls, name, None)
                if not target:
                    continue

                inherit_metadata(source=target, target=method)

    def __init__(
        self,
        *,
        api_client: ApiClient,
        config: Optional[Union[TConfig, dict]] = None,
    ):
        self._logger = logging.getLogger(f"{self.__module__}")
        self._api_client = api_client
        self.config = to_model_instance(config, self.Config)

    def _get_http_client(self, **kwargs) -> HttpxClient:
        return self._api_client.get_http_client(**kwargs)

    def _get_async_http_client(self, **kwargs):
        return self._api_client.get_async_http_client(**kwargs)

    def _log_method_execution(self, name: str, /, **kwargs):
        self._logger.debug("Calling %s with params: %s", name, kwargs)

    @staticmethod
    def _get_endpoint(
        endpoint: type[ApiEndpoint],
        **params: Union[int, str, Enum],
    ) -> str:
        target_endpoint = endpoint.path
        if not target_endpoint:
            raise ValueError("Endpoint was not found in the provided config.")

        for k, v in params.items():
            v = v.value if isinstance(v, Enum) else str(v)
            assert_is_not_empty_string(v)
            parameter_expression = f"{{{k}}}"
            if parameter_expression not in target_endpoint:
                raise ValueError(f"Variable '{k}' is not inside provided endpoint '{target_endpoint}'!")
            v = quote(v, safe=[])
            target_endpoint = target_endpoint.replace(parameter_expression, v)

        missing_path_parameters = re.findall(r"\{.*?}", target_endpoint)
        if missing_path_parameters:
            raise ValueError(
                f"Missing {','.join(missing_path_parameters)} parameters for '{target_endpoint}' endpoint."
            )

        return target_endpoint
