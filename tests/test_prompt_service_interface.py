import json
import os
import pathlib
from unittest.mock import MagicMock, patch 

import pytest

from genai.services import ServiceInterface
from genai.exceptions import GenAiException
from genai.credentials import Credentials
from genai.services import PromptTemplateManager
from tests.assets.response_helper import SimpleResponse

from genai.schemas.responses import WatsonxTemplate

@pytest.mark.unit
class TestPromptTemplateManager:
    def setup_method(self):
        self.credentials = Credentials("KEY", "ENDPOINT")
        self.string_template = """
            {{ instruction }}
            {{#examples}}
            
            {{input}}
            {{output}}
            
            {{/examples}}
            {{input}}
        """ 

    @patch("genai.services.RequestHandler.post")
    def test_save_template(self, mocked_post_request):
        name = "My template"
        t = self.string_template

        expected_resp = SimpleResponse.prompt_template(template=t, name=name)
        expected = MagicMock(status_code=200)
        expected.json.return_value = expected_resp
        mocked_post_request.return_value = expected

        template = PromptTemplateManager.save_template(credentials=self.credentials, template=t, name=name)

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == name

    @patch("genai.services.RequestHandler.put")
    def test_update_template(self, mocked_post_request):
        name = "My template"
        t = self.string_template

        expected_resp = SimpleResponse.prompt_template(template=t, name=name)
        expected = MagicMock(status_code=200)
        expected.json.return_value = expected_resp
        mocked_post_request.return_value = expected

        _id = expected_resp["results"]["id"]
        template = PromptTemplateManager.update_template(credentials=self.credentials, template=t, name=name, id=_id)

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == name

    @patch("genai.services.PromptTemplateManager.load_template_by_name")
    @patch("genai.services.PromptTemplateManager.load_template_by_id")
    def test_load_template(self, mock_load_by_id, mock_load_by_name):

        _id = "my_super_id"        
        PromptTemplateManager.load_template(credentials=self.credentials, id=_id)
        mock_load_by_id.assert_called_with(credentials=self.credentials, id=_id)
        
        _name = "my_super_name"
        PromptTemplateManager.load_template(credentials=self.credentials, name=_name)
        mock_load_by_name.assert_called_with(credentials=self.credentials, name=_name)

        error = "Provide either name or id of prompt to be fetch." + "\nIf you want to list all templates, use the load_all_templates method."
        with pytest.raises(GenAiException, match=error):
            PromptTemplateManager.load_template(credentials=self.credentials)

    @patch("genai.services.RequestHandler.get")
    def test_load_template_by_id(self, mock_get):
        name = "My template"
        t = self.string_template

        expected_resp = SimpleResponse.prompt_template(template=t, name=name)
        expected = MagicMock(status_code=200)
        expected.json.return_value = expected_resp
        mock_get.return_value = expected

        _id = expected_resp["results"]["id"]
        template = PromptTemplateManager.load_template_by_id(credentials=self.credentials, id=_id)

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == name

        
        

