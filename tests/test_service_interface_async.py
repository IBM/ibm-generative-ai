from unittest import TestCase
from unittest.mock import AsyncMock, patch

import pytest

from genai.exceptions import GenAiException
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate


@pytest.mark.unit
class TestServiceInterfaceAsync:
    def setup_method(self):
        # mock object for the API call
        self.service = ServiceInterface(service_url="http://SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    # GENERATE ASYNC
    @pytest.mark.asyncio
    @patch("genai.services.RequestHandler.async_generate")
    async def test_generate_async_api_call(self, mock: AsyncMock):
        expected_resp = SimpleResponse.generate(model=self.model, inputs=self.inputs)
        expected = AsyncMock(status_code=200, json=expected_resp)

        mock.return_value = expected
        resp = await self.service.async_generate(model=self.model, inputs=self.inputs)

        assert resp == expected
        assert resp.status_code == 200
        TestCase().assertDictEqual(resp.json, expected_resp)

    @pytest.mark.asyncio
    @patch("genai.services.RequestHandler.async_generate", side_effect=Exception("oh no, an exception"))
    async def test_generate_async_with_exception(self, mock):
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
    @patch("genai.services.RequestHandler.async_tokenize")
    async def test_tokenize_async_api_call(self, mock: AsyncMock):
        expected_resp = SimpleResponse.tokenize(model=self.model, inputs=self.inputs)
        expected = AsyncMock(status_code=200, json=expected_resp)

        mock.return_value = expected
        resp = await self.service.async_tokenize(model=self.model, inputs=self.inputs)

        assert resp == expected
        assert resp.status_code == 200

    @pytest.mark.asyncio
    @patch("genai.services.RequestHandler.async_tokenize", side_effect=Exception("oh no"))
    async def test_tokenize_async_with_exception(self, mock):
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
    @patch("genai.services.RequestHandler.async_get")
    async def test_history_async_api_call(self, mock: AsyncMock):
        expected_resp = SimpleResponse.history()
        expected = AsyncMock(status_code=200, json=expected_resp)

        mock.return_value = expected
        resp = await self.service.async_history()

        assert resp == expected
        assert resp.status_code == 200

    @pytest.mark.asyncio
    @patch("genai.services.RequestHandler.async_get", side_effect=Exception("oh no no"))
    async def test_history_async_with_exception(self, mock):
        with pytest.raises(GenAiException, match="oh no no"):
            await self.service.async_history()

    # TOU ASYNC
    @pytest.mark.asyncio
    @patch("genai.services.RequestHandler.async_patch")
    async def test_tou_async_api_call(self, mock: AsyncMock):
        expected_resp = SimpleResponse.terms_of_use()
        expected = AsyncMock(status_code=200, json=expected_resp)

        mock.return_value = expected
        resp = await self.service.async_terms_of_use(True)

        assert resp == expected
        assert resp.status_code == 200

    @pytest.mark.asyncio
    @patch("genai.services.RequestHandler.async_patch", side_effect=Exception("oh no no"))
    async def test_tou_async_with_exception(self, mock):
        with pytest.raises(BaseException, match="oh no no"):
            await self.service.async_terms_of_use(False)
