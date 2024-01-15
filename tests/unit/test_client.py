import logging

import pytest

from genai import Client, Credentials
from genai._utils.api_client import ApiClient, HttpTransportOptions
from genai.file.file_service import FileService
from genai.model.model_service import ModelService
from genai.prompt.prompt_service import PromptService
from genai.request.request_service import RequestService
from genai.text import TextService
from genai.tune import TuneService
from genai.user import UserService

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestClient:
    def _assert_invariant(self, client: Client):
        assert isinstance(client, Client)
        assert isinstance(client.text, TextService)
        assert isinstance(client.model, ModelService)
        assert isinstance(client.tune, TuneService)
        assert isinstance(client.prompt, PromptService)
        assert isinstance(client.user, UserService)
        assert isinstance(client.request, RequestService)
        assert isinstance(client.file, FileService)

    def test_basic_init_from_credentials(self, credentials: Credentials):
        client = Client(credentials=credentials)
        self._assert_invariant(client)

    def test_basic_init_from_api_client(self, credentials: Credentials):
        api_client = ApiClient(credentials=credentials)
        client = Client(api_client=api_client)
        self._assert_invariant(client)

    def test_custom_services(self, credentials: Credentials):
        class MyTextService(TextService):
            def dummy(self):
                return True

        class MyTuneService(TuneService):
            def dummy(self):
                return True

        services = Client.Services(TextService=MyTextService, TuneService=MyTuneService)
        client = Client(credentials=credentials, services=services)
        self._assert_invariant(client)
        assert isinstance(client.text, MyTextService)
        assert client.text.dummy()
        assert isinstance(client.tune, MyTuneService)
        assert client.tune.dummy()

    def test_custom_invalid_services(self, credentials: Credentials):
        class MyTextService(TuneService):  # TextService inherits from a bad class
            def dummy(self):
                return True

        with pytest.raises(ValueError):
            services = Client.Services(TextService=MyTextService)
            Client(credentials=credentials, services=services)

    def test_default_options(self, credentials: Credentials):
        config = Client.Config(api_client_config=ApiClient.Config(transport_options=HttpTransportOptions(retries=999)))
        client = Client(
            credentials=credentials,
            config=config,
        )
        self._assert_invariant(client)
        assert client._api_client.config.transport_options.retries == 999

    def test_default_options_from_dict(self, credentials: Credentials):
        config = {"api_client_config": {"transport_options": {"retries": 999}}}
        client = Client(credentials=credentials, config=config)
        self._assert_invariant(client)
        assert client._api_client.config.transport_options.retries == 999
