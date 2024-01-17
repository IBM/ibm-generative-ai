import logging

import pytest
from pydantic import BaseModel, ValidationError

from genai._generated.endpoints import ApiEndpoint
from genai._utils.api_client import ApiClient
from genai._utils.http_client.httpx_client import AsyncHttpxClient, HttpxClient
from genai._utils.service import BaseService
from genai._utils.shared_loop import shared_event_loop
from genai.credentials import Credentials

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestBaseService:
    @pytest.fixture
    def service(self, credentials: Credentials):
        class MyService(BaseService):
            pass

        api_client = ApiClient(credentials=credentials)
        service = MyService(api_client=api_client)
        self._assert_service_invariant(service)
        return service

    def _assert_service_invariant(self, service: BaseService):
        assert isinstance(service, BaseService)
        assert issubclass(service.Config, BaseModel)
        assert issubclass(service.Services, BaseModel)
        assert isinstance(service.config, service.Config)

    def create_endpoint(self, new_path: str):
        class MyEndpoint(ApiEndpoint):
            path: str = new_path
            method: str = "GET"
            version: str = "2023-11-22"

        return MyEndpoint

    def test_disallow_unknown_fields(self, credentials):
        class MyService(BaseService):
            pass

        with pytest.raises(ValidationError):
            service = MyService(api_client=ApiClient(credentials=credentials))
            self._assert_service_invariant(service)
            service.config.unknown_field = "x"

        with pytest.raises(ValidationError):
            service = MyService(
                api_client=ApiClient(credentials=credentials), config=MyService.Config(unknown_field="x")
            )

    def test_get_api_client(self, service):
        assert isinstance(service._get_http_client(), HttpxClient)
        with shared_event_loop:
            assert isinstance(service._get_async_http_client(), AsyncHttpxClient)

    def test_get_endpoint(self, service: BaseService):
        assert service._get_endpoint(self.create_endpoint("/v2/a")) == "/v2/a"
        assert (
            service._get_endpoint(self.create_endpoint("/v2/{id}/content/{type}"), id="a", type="b")
            == "/v2/a/content/b"
        )

        with pytest.raises(ValueError):
            assert service._get_endpoint(endpoint=self.create_endpoint("/v2/{id}"))

        with pytest.raises(TypeError):
            assert service._get_endpoint()

        with pytest.raises(TypeError):
            service._get_endpoint(id="1")
