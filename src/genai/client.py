from __future__ import annotations

from typing import Optional, Type, overload

from genai._types import ModelLike
from genai._utils.api_client import ApiClient
from genai._utils.api_client import BaseConfig as ApiClientConfig
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai._utils.general import to_model_instance
from genai.credentials import Credentials
from genai.file import FileService
from genai.model import ModelService
from genai.prompt import PromptService
from genai.request import RequestService
from genai.text import TextService
from genai.tune import TuneService
from genai.user import UserService

__all__ = ["Client", "BaseConfig", "BaseServices"]


class BaseServices(BaseServiceServices):
    """Appropriate services used by the Client"""

    TextService: Type[TextService] = TextService
    RequestService: Type[RequestService] = RequestService
    TuneService: Type[TuneService] = TuneService
    ModelService: Type[ModelService] = ModelService
    FileService: Type[FileService] = FileService
    PromptService: Type[PromptService] = PromptService
    UserService: Type[UserService] = UserService


class BaseConfig(BaseServiceConfig):
    """Client's configuration model"""

    api_client_config: Optional[ModelLike[ApiClientConfig]] = None


class Client(BaseService[BaseConfig, BaseServices]):
    """
    The `Client` class provides an interface for interacting with various services through an API client.
    It can be initialized with either an `api_client` or `credentials` along with optional configurations and services.

    Example::

        from genai import Credentials, Client

        credentials = Credentials.from_env()
        client = Client(credentials=credentials)

    Attributes:
        text: An instance of the `TextService` class for text-related operations.
        request: An instance of the `RequestService` class for making request-related operations.
        tune: An instance of the `TuneService` class for tuning models.
        model: An instance of the `ModelService` class for managing models.
        file: An instance of the `FileService` class for managing files.
        prompt: An instance of the `PromptService` class for working with prompts.
        user: An instance of the `UserService` class for managing user-related operations.
    """

    Config = BaseConfig
    Services = BaseServices

    @overload
    def __init__(
        self,
        *,
        api_client: ApiClient,
        config: Optional[ModelLike[BaseConfig]] = None,
        services: Optional[BaseServices] = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        credentials: Credentials,
        config: Optional[ModelLike[BaseConfig]] = None,
        services: Optional[BaseServices] = None,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        credentials: Optional[Credentials] = None,
        api_client: Optional[ApiClient] = None,
        config: Optional[ModelLike[BaseConfig]] = None,
        services: Optional[BaseServices] = None,
    ) -> None:
        """
        Args:
            credentials: The credentials used to authenticate the API client.
            api_client: The API client used to make requests to the API.
            config: The configuration for the API client.
            services: The services object containing instances of various service classes.

        Raises:
            ValueError: Either 'api_client' or 'credentials' needs to be passed.

        Note:
            The `api_client` parameter must be provided either directly or through `credentials`.
            If no `services` parameter is provided, the client will use the default one.
        """
        config = to_model_instance(config, self.Config)

        if (not api_client and not credentials) or (api_client and credentials):
            raise ValueError("Either 'api_client' or 'credentials' needs to passed.")

        if not api_client:
            assert credentials
            api_client = ApiClient(credentials=credentials, config=config.api_client_config)

        assert api_client and config
        super().__init__(api_client=api_client, config=config)

        if not services:
            services = self.Services()

        self.text: TextService = services.TextService(api_client=api_client)
        self.request: RequestService = services.RequestService(api_client=api_client)
        self.tune: TuneService = services.TuneService(api_client=api_client)
        self.model: ModelService = services.ModelService(api_client=api_client)
        self.file: FileService = services.FileService(api_client=api_client)
        self.prompt: PromptService = services.PromptService(api_client=api_client)
        self.user: UserService = services.UserService(api_client=api_client)
