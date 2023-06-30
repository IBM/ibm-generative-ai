from unittest.mock import MagicMock, patch

import pytest

from genai.credentials import Credentials
from genai.exceptions import GenAiException
from genai.schemas.responses import WatsonxTemplate, WatsonxTemplatesResponse
from genai.services import PromptTemplateManager
from tests.assets.response_helper import SimpleResponse


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
        self.name = "My template"

        self.expected_resp = SimpleResponse.prompt_template(template=self.string_template, name=self.name)

        self.template = WatsonxTemplate.parse_obj(self.expected_resp["results"])
        self.all_templates = WatsonxTemplatesResponse.parse_obj({"results": [self.template], "totalCount": 1})

    @patch("genai.services.RequestHandler.post")
    def test_save_template(self, mocked_post_request):
        expected = MagicMock(status_code=200)
        expected.json.return_value = self.expected_resp
        mocked_post_request.return_value = expected

        template = PromptTemplateManager.save_template(
            credentials=self.credentials, template=self.string_template, name=self.name
        )

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == self.name

    @patch("genai.services.RequestHandler.post", side_effect=Exception("Ooops"))
    def test_save_template_exception(self, mocked_post_request):
        expected = MagicMock(status_code=200)
        expected.json.return_value = self.expected_resp
        mocked_post_request.return_value = expected

        with pytest.raises(GenAiException, match="Ooops"):
            PromptTemplateManager.save_template(
                credentials=self.credentials, template=self.string_template, name=self.name
            )

    @patch("genai.services.RequestHandler.put")
    def test_update_template(self, mocked_post_request):
        expected = MagicMock(status_code=200)
        expected.json.return_value = self.expected_resp
        mocked_post_request.return_value = expected

        _id = self.template.id
        template = PromptTemplateManager.update_template(
            credentials=self.credentials, template=self.string_template, name=self.name, id=_id
        )

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == self.name

    @patch("genai.services.RequestHandler.put", side_effect=Exception("Ooops"))
    def test_update_template_exception(self, mocked_post_request):
        expected = MagicMock(status_code=200)
        expected.json.return_value = self.expected_resp
        mocked_post_request.return_value = expected

        with pytest.raises(GenAiException, match="Ooops"):
            _id = self.template.id
            PromptTemplateManager.update_template(
                credentials=self.credentials, template=self.string_template, name=self.name, id=_id
            )

    @patch("genai.services.PromptTemplateManager.load_template_by_name")
    @patch("genai.services.PromptTemplateManager.load_template_by_id")
    def test_load_template(self, mock_load_by_id, mock_load_by_name):
        _id = "my_super_id"
        PromptTemplateManager.load_template(credentials=self.credentials, id=_id)
        mock_load_by_id.assert_called_with(credentials=self.credentials, id=_id)

        _name = "my_super_name"
        PromptTemplateManager.load_template(credentials=self.credentials, name=_name)
        mock_load_by_name.assert_called_with(credentials=self.credentials, name=_name)

        error = (
            "Provide either name or id of prompt to be fetch."
            + "\nIf you want to list all templates, use the load_all_templates method."
        )
        with pytest.raises(GenAiException, match=error):
            PromptTemplateManager.load_template(credentials=self.credentials)

    @patch("genai.services.RequestHandler.get")
    def test_load_all_template(self, mock_get):
        expected = MagicMock(status_code=200)
        expected.json.return_value = {"results": [self.template.dict()], "totalCount": 1}
        mock_get.return_value = expected

        resp = PromptTemplateManager.load_all_templates(credentials=self.credentials)

        assert isinstance(resp, WatsonxTemplatesResponse)
        assert isinstance(resp.results[0], WatsonxTemplate)
        assert resp.totalCount == 1

    @patch("genai.services.RequestHandler.get")
    def test_load_all_template_404(self, mock_get):
        expected = MagicMock(status_code=404)
        mock_get.return_value = expected

        with pytest.raises(GenAiException):
            PromptTemplateManager.load_all_templates(credentials=self.credentials)

    @patch("genai.services.RequestHandler.get")
    def test_load_template_by_id(self, mock_get):
        expected = MagicMock(status_code=200)
        expected.json.return_value = self.expected_resp
        mock_get.return_value = expected

        _id = self.template.id
        template = PromptTemplateManager.load_template_by_id(credentials=self.credentials, id=_id)

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == self.name

    @patch("genai.services.RequestHandler.get")
    def test_load_template_by_id_not_found(self, mock_get):
        expected = MagicMock(status_code=404)
        expected.json.return_value = self.expected_resp
        mock_get.return_value = expected

        with pytest.raises(Exception):
            _id = self.template.id
            PromptTemplateManager.load_template_by_id(credentials=self.credentials, id=_id)

    @patch("genai.services.PromptTemplateManager.load_all_templates")
    @patch("genai.services.RequestHandler.get")
    def test_load_template_by_name(self, mock_get, mock_load_all_templates):
        expected = MagicMock(status_code=200)
        mock_get.return_value = expected
        mock_load_all_templates.return_value = self.all_templates

        name = self.template.name
        template = PromptTemplateManager.load_template_by_name(credentials=self.credentials, name=name)

        assert isinstance(template, WatsonxTemplate)
        assert template.id == self.template.id
        assert template.name == self.template.name

    @patch("genai.services.PromptTemplateManager.load_all_templates")
    @patch("genai.services.RequestHandler.get")
    def test_load_template_by_name_not_found(self, mock_get, mock_load_all_templates):
        no_templates = WatsonxTemplatesResponse.parse_obj({"results": [], "totalCount": 0})

        expected = MagicMock(status_code=200)
        mock_get.return_value = expected
        mock_load_all_templates.return_value = no_templates

        name = self.template.name
        with pytest.raises(GenAiException, match=f"No template found with name {name}"):
            PromptTemplateManager.load_template_by_name(credentials=self.credentials, name=name)

    @patch("genai.services.PromptTemplateManager.load_all_templates")
    @patch("genai.services.RequestHandler.get")
    def test_load_template_by_name_too_many_found(self, mock_get, mock_load_all_templates):
        no_templates = WatsonxTemplatesResponse.parse_obj({"results": [self.template, self.template], "totalCount": 2})

        expected = MagicMock(status_code=200)
        mock_get.return_value = expected
        mock_load_all_templates.return_value = no_templates

        name = self.template.name
        with pytest.raises(Exception, match=f"More than one template found with name {name}"):
            PromptTemplateManager.load_template_by_name(credentials=self.credentials, name=name)

    @patch("genai.services.PromptTemplateManager.delete_template_by_name")
    @patch("genai.services.PromptTemplateManager.delete_template_by_id")
    def test_delete_template(self, mock_delete_by_id, mock_delete_by_name):
        _id = "my_super_id"
        PromptTemplateManager.delete_template(credentials=self.credentials, id=_id)
        mock_delete_by_id.assert_called_with(credentials=self.credentials, id=_id)

        _name = "my_super_name"
        PromptTemplateManager.delete_template(credentials=self.credentials, name=_name)
        mock_delete_by_name.assert_called_with(credentials=self.credentials, name=_name)

        error = "Provide either name or id of prompt to be deleted."
        with pytest.raises(GenAiException, match=error):
            PromptTemplateManager.delete_template(credentials=self.credentials)

    @patch("genai.services.RequestHandler.delete")
    def test_delete_template_by_id(self, mock_delete):
        expected = MagicMock(status_code=204)
        mock_delete.return_value = expected

        _id = "prompt_template_id"
        template = PromptTemplateManager.delete_template_by_id(credentials=self.credentials, id=_id)

        assert isinstance(template, str)
        assert template == _id

    @patch("genai.services.RequestHandler.delete")
    def test_delete_template_by_id_not_found(self, mock_delete):
        expected = MagicMock(status_code=404)
        mock_delete.return_value = expected

        with pytest.raises(Exception):
            _id = "prompt_template_id"
            PromptTemplateManager.delete_template_by_id(credentials=self.credentials, id=_id)

    @patch("genai.services.PromptTemplateManager.load_all_templates")
    @patch("genai.services.RequestHandler.delete")
    def test_delete_template_by_name(self, mock_delete, mock_load_all_templates):
        expected = MagicMock(status_code=204)
        mock_delete.return_value = expected
        mock_load_all_templates.return_value = self.all_templates

        _id = self.template.id
        name = self.template.name

        template = PromptTemplateManager.delete_template_by_name(credentials=self.credentials, name=name)

        assert isinstance(template, str)
        assert template == _id

    @patch("genai.services.PromptTemplateManager.load_all_templates")
    @patch("genai.services.RequestHandler.delete")
    def test_delete_template_by_name_not_found(self, mock_delete, mock_load_all_templates):
        no_templates = WatsonxTemplatesResponse.parse_obj({"results": [], "totalCount": 0})

        expected = MagicMock(status_code=204)
        mock_delete.return_value = expected
        mock_load_all_templates.return_value = no_templates

        name = "not the template you are looking for"
        with pytest.raises(Exception, match=f"No template found for name {name}"):
            PromptTemplateManager.delete_template_by_name(credentials=self.credentials, name=name)

    @patch("genai.services.PromptTemplateManager.load_all_templates")
    @patch("genai.services.RequestHandler.delete")
    def test_delete_template_by_name_too_many_found(self, mock_delete, mock_load_all_templates):
        all_templates = WatsonxTemplatesResponse.parse_obj({"results": [self.template, self.template], "totalCount": 2})

        expected = MagicMock(status_code=204)
        mock_delete.return_value = expected
        mock_load_all_templates.return_value = all_templates

        name = self.template.name
        with pytest.raises(Exception, match=f"More than one template found for name {name}"):
            PromptTemplateManager.delete_template_by_name(credentials=self.credentials, name=name)

    @patch("genai.services.RequestHandler.post")
    def test_render_template(self, mock_post):
        expected = MagicMock(status_code=200)
        expected.json.return_value = {"results": ["rendered output 1", "rendered output 2"]}
        mock_post.return_value = expected

        results = PromptTemplateManager.render_watsonx_prompts(
            credentials=self.credentials, inputs=["some inputs"], data={}
        )

        assert len(results) == 2
        assert isinstance(results[0], str)

    @patch("genai.services.RequestHandler.post")
    def test_render_template_exception(self, mock_post):
        mock_post.return_value = MagicMock(status_code=404)

        with pytest.raises(GenAiException):
            PromptTemplateManager.render_watsonx_prompts(credentials=self.credentials, inputs=["some inputs"], data={})
