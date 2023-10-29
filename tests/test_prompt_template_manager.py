from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from genai.credentials import Credentials
from genai.exceptions import GenAiException
from genai.routers.prompt_template import PromptTemplateRouter
from genai.schemas.responses import WatsonxTemplate, WatsonxTemplatesResponse
from genai.services import PromptTemplateManager
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint


@pytest.mark.unit
class TestPromptTemplateManager:
    def setup_method(self):
        self.credentials = Credentials("KEY")
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

        self.template = WatsonxTemplate.model_validate(self.expected_resp["results"])
        #  datetime is not serializable by default, we replace with a valid datetime string
        self.template.created_at = "2023-05-08T11:51:18.000Z"
        self.all_templates = WatsonxTemplatesResponse.model_validate({"results": [self.template], "totalCount": 1})

    def test_save_template(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES), method="POST", json=self.expected_resp
        )

        template = PromptTemplateManager.save_template(
            credentials=self.credentials, template=self.string_template, name=self.name
        )

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == self.name

    def test_save_template_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(
            Exception("Ooops"), url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES), method="POST"
        )

        with pytest.raises(GenAiException, match="Ooops"):
            PromptTemplateManager.save_template(
                credentials=self.credentials, template=self.string_template, name=self.name
            )

    def test_update_template(self, httpx_mock: HTTPXMock):
        _id = self.template.id
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES, _id), method="PUT", json=self.expected_resp
        )

        template = PromptTemplateManager.update_template(
            credentials=self.credentials, template=self.string_template, name=self.name, id=_id
        )

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == self.name

    def test_update_template_exception(self, httpx_mock: HTTPXMock):
        _id = self.template.id
        httpx_mock.add_exception(
            Exception("Ooops"), url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES, _id), method="PUT"
        )
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

    def test_load_all_template(self, httpx_mock: HTTPXMock):
        expected = {"results": [self.template.model_dump()], "totalCount": 1}

        httpx_mock.add_response(url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES), method="GET", json=expected)

        resp = PromptTemplateManager.load_all_templates(credentials=self.credentials)

        assert isinstance(resp, WatsonxTemplatesResponse)
        assert isinstance(resp.results[0], WatsonxTemplate)
        assert resp.totalCount == 1

    def test_load_all_template_404(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES), method="GET", status_code=404
        )

        with pytest.raises(GenAiException):
            PromptTemplateManager.load_all_templates(credentials=self.credentials)

    def test_load_template_by_id(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES, self.template.id),
            method="GET",
            json=self.expected_resp,
        )

        _id = self.template.id
        template = PromptTemplateManager.load_template_by_id(credentials=self.credentials, id=_id)

        assert isinstance(template, WatsonxTemplate)
        assert template.value == self.string_template
        assert template.name == self.name

    def test_load_template_by_id_not_found(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES, self.template.id),
            method="GET",
            status_code=404,
        )

        with pytest.raises(Exception):
            _id = self.template.id
            PromptTemplateManager.load_template_by_id(credentials=self.credentials, id=_id)

    def test_load_template_by_name(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES),
            method="GET",
            json=self.all_templates.model_dump(),
        )

        name = self.template.name
        template = PromptTemplateManager.load_template_by_name(credentials=self.credentials, name=name)

        assert isinstance(template, WatsonxTemplate)
        assert template.id == self.template.id
        assert template.name == self.template.name

    def test_load_template_by_name_not_found(self, httpx_mock: HTTPXMock):
        no_templates = {"results": [], "totalCount": 0}

        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES), method="GET", json=no_templates
        )

        name = self.template.name
        with pytest.raises(GenAiException, match=f"No template found with name {name}"):
            PromptTemplateManager.load_template_by_name(credentials=self.credentials, name=name)

    def test_load_template_by_name_too_many_found(self, httpx_mock: HTTPXMock):
        no_templates = {"results": [self.template.model_dump(), self.template.model_dump()], "totalCount": 2}
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES), method="GET", json=no_templates
        )
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

    def test_delete_template_by_id(self, httpx_mock: HTTPXMock):
        _id = "prompt_template_id"
        httpx_mock.add_response(url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES, _id), method="DELETE")

        template = PromptTemplateManager.delete_template_by_id(credentials=self.credentials, id=_id)

        assert isinstance(template, str)
        assert template == _id

    def test_delete_template_by_id_not_found(self, httpx_mock: HTTPXMock):
        _id = "prompt_template_id"
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES, self.template.id),
            method="DELETE",
            status_code=404,
        )

        with pytest.raises(Exception):
            PromptTemplateManager.delete_template_by_id(credentials=self.credentials, id=_id)

    def test_delete_template_by_name(self, httpx_mock: HTTPXMock):
        _id = self.template.id
        name = self.template.name

        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES),
            method="GET",
            json=self.all_templates.model_dump(),
        )
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES, _id), method="DELETE", json=_id
        )
        template = PromptTemplateManager.delete_template_by_name(credentials=self.credentials, name=name)

        assert isinstance(template, str)
        assert template == _id

    def test_delete_template_by_name_not_found(self, httpx_mock: HTTPXMock):
        no_templates = {"results": [], "totalCount": 0}

        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES), method="GET", json=no_templates
        )

        name = "not the template you are looking for"
        with pytest.raises(Exception, match=f"No template found for name {name}"):
            PromptTemplateManager.delete_template_by_name(credentials=self.credentials, name=name)

    def test_delete_template_by_name_too_many_found(self, httpx_mock: HTTPXMock):
        template_dict = self.template.model_dump()
        all_templates = {"results": [template_dict, template_dict], "totalCount": 2}

        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES), method="GET", json=all_templates
        )
        httpx_mock.add_response(
            url=match_endpoint(PromptTemplateRouter.PROMPT_TEMPLATES, self.template.id), method="DELETE"
        )

        name = self.template.name
        with pytest.raises(Exception, match=f"More than one template found for name {name}"):
            PromptTemplateManager.delete_template_by_name(credentials=self.credentials, name=name)

    def test_render_template(self, httpx_mock: HTTPXMock):
        expected = {"results": ["rendered output 1", "rendered output 2"]}
        httpx_mock.add_response(
            url=match_endpoint(f"{PromptTemplateRouter.PROMPT_TEMPLATES}/output"), method="POST", json=expected
        )

        results = PromptTemplateManager.render_watsonx_prompts(
            credentials=self.credentials, inputs=["some inputs"], data={}
        )

        assert len(results) == 2
        assert isinstance(results[0], str)

    def test_render_template_exception(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(
            Exception("Oops"), url=match_endpoint(f"{PromptTemplateRouter.PROMPT_TEMPLATES}/output"), method="POST"
        )

        with pytest.raises(GenAiException, match="Oops"):
            PromptTemplateManager.render_watsonx_prompts(credentials=self.credentials, inputs=["some inputs"], data={})
