from genai import Credentials
from genai.exceptions import GenAiException
from genai.schemas.responses import (
    WatsonxRenderedPrompts,
    WatsonxTemplate,
    WatsonxTemplatesResponse,
)
from genai.services import ServiceInterface


class PromptTemplateManager:
    @staticmethod
    def save_template(template: str, name: str, credentials: Credentials) -> WatsonxTemplate:
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

        try:
            response = service._prompt_templating.prompt_templates(name, value=template)
            if response.status_code == 200:
                response_result = WatsonxTemplate(**response.json()["results"])
                return response_result
            raise GenAiException(response)
        except Exception as ex:
            raise GenAiException(ex)

    @staticmethod
    def update_template(credentials: Credentials, id: str, name: str, template: str) -> WatsonxTemplate:
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

        try:
            response = service._prompt_templating.update_prompt_templates(id=id, name=name, value=template)
            if response.status_code == 200:
                response_result = WatsonxTemplate(**response.json()["results"])
                return response_result
            raise GenAiException(response)
        except Exception as ex:
            raise GenAiException(ex)

    @staticmethod
    def render_watsonx_prompts(credentials: Credentials, inputs: list = None, data: dict = {}) -> list[str]:
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

        try:
            response = service._prompt_templating.prompt_output(inputs, template=data)
            if response.status_code == 200:
                response_result = WatsonxRenderedPrompts(**response.json())
                return response_result.results
            raise GenAiException(response)
        except Exception as ex:
            raise GenAiException(ex)

    @staticmethod
    def load_template(credentials: Credentials, id: str = None, name: str = None) -> WatsonxTemplate:
        if id:
            return PromptTemplateManager.load_template_by_id(credentials=credentials, id=id)
        if name:
            return PromptTemplateManager.load_template_by_name(credentials=credentials, name=name)
        else:
            raise GenAiException(
                "Provide either name or id of prompt to be fetch."
                + "\nIf you want to list all templates, use the load_all_templates method."
            )

    @staticmethod
    def load_all_templates(credentials: Credentials) -> WatsonxTemplatesResponse:
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

        try:
            response = service._prompt_templating.get_prompt_templates()
            if response.status_code == 200:
                return WatsonxTemplatesResponse(**response.json())
            raise GenAiException(response)
        except Exception as ex:
            raise GenAiException(ex)

    @staticmethod
    def load_template_by_id(credentials: Credentials, id: str) -> WatsonxTemplate:
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

        try:
            response = service._prompt_templating.get_prompt_templates(id)
            if response.status_code == 200:
                return WatsonxTemplate(**response.json()["results"])
            raise GenAiException(response)
        except Exception as ex:
            raise GenAiException(ex)

    @staticmethod
    def load_template_by_name(credentials: Credentials, name: str) -> WatsonxTemplate:
        try:
            saved_templates = PromptTemplateManager.load_all_templates(credentials=credentials)
            template = list(filter(lambda tp: tp.name == name, saved_templates.results))

            if len(template) == 1:
                return template[0]

            if len(template) == 0:
                raise Exception(f"No template found with name {name}")
            raise Exception(f"More than one template found with name {name}")
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def delete_template(credentials: Credentials, id: str = None, name: str = None) -> str:
        if id:
            return PromptTemplateManager.delete_template_by_id(credentials=credentials, id=id)
        elif name:
            return PromptTemplateManager.delete_template_by_name(credentials=credentials, name=name)
        else:
            raise GenAiException("Provide either name or id of prompt to be deleted.")

    @staticmethod
    def delete_template_by_id(credentials: Credentials, id: str) -> str:
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

        try:
            response = service._prompt_templating.delete_prompt_templates(id)
            if response.status_code == 204:
                return id
            raise GenAiException(response)
        except GenAiException as ex:
            raise Exception(ex)

    @staticmethod
    def delete_template_by_name(credentials: Credentials, name: str) -> str:
        try:
            saved_templates = PromptTemplateManager.load_all_templates(credentials=credentials)
            template = list(filter(lambda tp: tp.name == name, saved_templates.results))

            if len(template) == 1:
                return PromptTemplateManager.delete_template_by_id(credentials=credentials, id=template[0].id)
            if len(template) == 0:
                raise Exception(f"No template found for name {name}")
            raise Exception(f"More than one template found for name {name}")
        except GenAiException as e:
            raise Exception(e)
