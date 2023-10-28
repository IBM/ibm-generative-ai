from unittest import TestCase

import pytest
from pytest_httpx import HTTPXMock

from genai.exceptions import GenAiException
from genai.services import ServiceInterface
from genai.services.connection_manager import ConnectionManager
from genai.utils.request_utils import match_endpoint
from tests.assets.response_helper import SimpleResponse

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate


@pytest.mark.unit
class TestServiceInterfaceAsync:
    def setup_class(self):
        ConnectionManager.make_generate_client()
        ConnectionManager.make_tokenize_client()

    def setup_method(self):
        # mock object for the API call
        self.service = ServiceInterface(service_url="http://SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    # GENERATE ASYNC
    @pytest.mark.asyncio
    async def test_generate_async_api_call(self, httpx_mock: HTTPXMock):
        expected_resp = SimpleResponse.generate(model=self.model, inputs=self.inputs)
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=expected_resp)

        resp = await self.service.async_generate(model=self.model, inputs=self.inputs)

        assert httpx_mock.get_request(url=match_endpoint(ServiceInterface.GENERATE), method="POST") is not None
        assert resp.is_success
        TestCase().assertDictEqual(resp.json(), expected_resp)

    @pytest.mark.asyncio
    async def test_generate_async_with_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(
            Exception("oh no, an exception"), url=match_endpoint(ServiceInterface.GENERATE), method="POST"
        )
        with pytest.raises(GenAiException, match="oh no, an exception"):
            await self.service.async_generate(model=self.model, inputs=self.inputs)

    @pytest.mark.asyncio
    async def test_generate_async_with_no_model(self):
        with pytest.raises(TypeError):
            await self.service.async_generate(inputs=self.inputs)

    @pytest.mark.asyncio
    async def test_generate_async_with_no_input(self):
        with pytest.raises(TypeError):
            await self.service.async_generate(model=self.model)

    @pytest.mark.asyncio
    async def test_generate_async_empty_body(self):
        with pytest.raises(TypeError):
            await self.service.async_generate()

    # TOKENIZE  ASYNC
    @pytest.mark.asyncio
    async def test_tokenize_async_api_call(self, httpx_mock: HTTPXMock):
        expected_resp = SimpleResponse.tokenize(model=self.model, inputs=self.inputs)
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.TOKENIZE), method="POST", json=expected_resp)

        resp = await self.service.async_tokenize(model=self.model, inputs=self.inputs)

        assert httpx_mock.get_request(url=match_endpoint(ServiceInterface.TOKENIZE), method="POST") is not None
        assert resp.is_success

    @pytest.mark.asyncio
    async def test_tokenize_async_with_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(Exception("oh no"), url=match_endpoint(ServiceInterface.TOKENIZE), method="POST")
        with pytest.raises(GenAiException, match="oh no"):
            await self.service.async_tokenize(model=self.model, inputs=self.inputs)

    @pytest.mark.asyncio
    async def test_tokenize_async_with_no_model(self):
        with pytest.raises(TypeError):
            await self.service.async_tokenize(inputs=self.inputs)

    @pytest.mark.asyncio
    async def test_tokenize_async_with_no_input(self):
        with pytest.raises(TypeError):
            await self.service.async_tokenize(model=self.model)

    @pytest.mark.asyncio
    async def test_tokenize_async_empty_body(self):
        with pytest.raises(TypeError):
            await self.service.async_tokenize()

    # HISTRORY ASYNC
    @pytest.mark.asyncio
    async def test_history_async_api_call(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=match_endpoint(ServiceInterface.HISTORY), method="GET", json=SimpleResponse.history()
        )
        resp = await self.service.async_history()

        assert httpx_mock.get_request(url=match_endpoint(ServiceInterface.HISTORY), method="GET") is not None
        assert resp.is_success

    @pytest.mark.asyncio
    async def test_history_async_with_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(Exception("oh no no"), url=match_endpoint(ServiceInterface.HISTORY), method="GET")
        with pytest.raises(GenAiException, match="oh no no"):
            await self.service.async_history()

    # TOU ASYNC
    @pytest.mark.asyncio
    async def test_tou_async_api_call(self, httpx_mock: HTTPXMock):
        expected_resp = SimpleResponse.terms_of_use()
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.TOU), method="PATCH", json=expected_resp)

        resp = await self.service.async_terms_of_use(True)

        assert httpx_mock.get_request(url=match_endpoint(ServiceInterface.TOU), method="PATCH") is not None
        assert resp.is_success

    @pytest.mark.asyncio
    async def test_tou_async_with_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(Exception("oh no no"), url=match_endpoint(ServiceInterface.TOU), method="PATCH")
        with pytest.raises(BaseException, match="oh no no"):
            await self.service.async_terms_of_use(False)

    @pytest.mark.asyncio
    async def test_cleanup(self):
        await ConnectionManager.delete_generate_client()
        await ConnectionManager.delete_tokenize_client()
