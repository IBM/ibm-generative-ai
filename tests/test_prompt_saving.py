from unittest.mock import MagicMock, patch

import pytest

from genai import Credentials
from genai.exceptions import GenAiException
from genai.routers import PromptSavingRouter
from genai.schemas import PromptListParams

# from genai.schemas.responses import PromptResponse
from genai.services.prompt_manager import PromptManager
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestPromptSaving:
    def setup_method(self):
        self.service = PromptSavingRouter(service_url="API_URL", api_key="API_KEY")

    @pytest.fixture
    def params(self):
        return PromptListParams(limit=1, offset=0)

    @pytest.fixture
    def creds(self):
        return Credentials("GENAI_APY_KEY")

    @patch("genai.services.RequestHandler.get")
    def test_prompt_list_api_call(self, mocker, params, creds):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.prompt_saving()
        mocker.return_value = mock_response

        pt = self.service.list_prompts(params=params)
        assert pt == mock_response

    def test_prompt_list_api_call_with_wrong_params(self):
        with pytest.raises(GenAiException) as e:
            self.service.list_prompts(params="params")
            assert e.message == "params must be of type PromptListParams."

    def test_get_prompt_api_call_wrong_id(self):
        with pytest.raises(GenAiException) as e:
            self.service.get_prompt(id=123)
            assert e.message == "File not found, id must be of type str"

    def test_delete_prompt_api_call_wrong_id(self):
        with pytest.raises(GenAiException) as e:
            self.service.delete_prompt(id=123)
            assert e.message == "File not found, id must be of type str"

    @patch("genai.services.RequestHandler.delete")
    def test_delete_prompt(self, mocker, creds):
        expected_response = {"status": "success"}
        response = MagicMock(status_code=204)
        response.json.return_value = expected_response
        mocker.return_value = response

        response = PromptManager.delete_prompt(creds=creds, id="id")
        assert response == expected_response
