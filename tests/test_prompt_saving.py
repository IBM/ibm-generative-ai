from unittest.mock import MagicMock, patch

import pytest

from genai import Credentials
from genai.exceptions import GenAiException
from genai.routers import PromptSavingRouter
from genai.schemas import PromptListParams
from genai.schemas.responses import PromptListResponse, PromptResponse
from genai.services.prompt_manager import PromptManager
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestPromptSaving:
    def setup_method(self):
        self.service_router = PromptSavingRouter(service_url="API_URL", api_key="API_KEY")

    @pytest.fixture
    def params(self):
        return PromptListParams(limit=1, offset=0)

    @pytest.fixture
    def creds(self):
        return Credentials("GENAI_APY_KEY")

    # test prompt list
    @patch("genai.services.RequestHandler.get")
    def test_prompt_list_api_call(self, mocker, params, creds):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.prompt_saving()
        mocker.return_value = mock_response

        pt = self.service_router.list_prompts(params=params)
        assert pt == mock_response

    def test_prompt_list_api_call_with_wrong_params(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.list_prompts(params="params")
            assert e.message == "params must be of type PromptListParams."

    @patch("genai.services.RequestHandler.get")
    def test_prompt_list(self, mocker, params, creds):
        list_response = SimpleResponse.prompt_saving(params=params)
        expected_response = PromptListResponse(**list_response)

        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = list_response
        mocker.return_value = mock_response

        pt = PromptManager.list_prompts(creds=creds)
        assert pt == expected_response

    # test prompt get
    def test_get_prompt_api_call_wrong_id(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.get_prompt(id=123)
            assert e.message == "File not found, id must be of type str"

    @patch("genai.services.RequestHandler.get")
    def test_get_prompt(self, mocker, creds):
        get_response = SimpleResponse.prompt_saving(id="id")
        expected_response = PromptResponse(**get_response["results"])

        response = MagicMock(status_code=200)
        response.json.return_value = get_response
        mocker.return_value = response

        response = PromptManager.get_prompt(creds=creds, id="id")
        assert response == expected_response

    @patch("genai.services.RequestHandler.get")
    def test_get_prompt_api_call(self, mocker):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.prompt_saving()
        mocker.return_value = mock_response

        pt = self.service_router.get_prompt(id="id")
        assert pt == mock_response

    # TODO: test prompt create

    # TODO: test update prompt

    # test prompt delete
    def test_delete_prompt_api_call_wrong_id(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.delete_prompt(id=123)
            assert e.message == "File not found, id must be of type str"

    @patch("genai.services.RequestHandler.delete")
    def test_delete_prompt(self, mocker, creds):
        expected_response = {"status": "success"}
        response = MagicMock(status_code=204)
        response.json.return_value = expected_response
        mocker.return_value = response

        response = PromptManager.delete_prompt(creds=creds, id="id")
        assert response == expected_response
