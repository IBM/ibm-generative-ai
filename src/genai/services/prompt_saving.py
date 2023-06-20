from genai.exceptions import GenAiException
from genai.options import Options
from genai.schemas import GenerateParams, PromptListParams, PromptTemplateParams
from genai.services import RequestHandler, ServiceInterface


class PromptSaving:
    PROMPT_SAVING = "/prompts"

    def __init__(self, service_url: str, api_key: str) -> None:
        self.service_interface = ServiceInterface(service_url, api_key)

    def list_prompts(self, params: PromptListParams = None):
        try:
            endpoint = self.service_interface.service_url + PromptSaving.PROMPT_SAVING
            return RequestHandler.get(endpoint, key=self.service_interface.key, parameters=params)
        except Exception as e:
            raise GenAiException(e)

    def create_prompt(
        self,
        name: str,
        model_id: str,
        template: dict,
        input: str = None,
        output: str = None,
        parameters: GenerateParams = None,
    ):
        try:
            endpoint = self.service_interface.service_url + PromptSaving.PROMPT_SAVING
            return RequestHandler.post(
                endpoint,
                key=self.service_interface.key,
                model_id=model_id,
                parameters=parameters,
                options=Options(name=name, template=template, input=input, output=output),
            )
        except Exception as e:
            raise GenAiException(e)

    def update_prompt(
        self, id: str, name: str, model_id: str, template: PromptTemplateParams, input: str = None, output: str = None
    ):
        try:
            endpoint = self.service_interface.service_url + PromptSaving.PROMPT_SAVING + "/" + id
            return RequestHandler.put(
                endpoint,
                key=self.service_interface.key,
                options=Options(name=name, model_id=model_id, template=template, input=input, output=output),
            )
        except Exception as e:
            raise GenAiException(e)

    def get_prompt(self, id: str):
        try:
            endpoint = self.service_interface.service_url + PromptSaving.PROMPT_SAVING + "/" + id
            return RequestHandler.get(endpoint, key=self.service_interface.key)
        except Exception as e:
            raise GenAiException(e)

    def delete_prompt(self, id: str):
        try:
            endpoint = self.service_interface.service_url + PromptSaving.PROMPT_SAVING + "/" + id
            return RequestHandler.delete(endpoint, key=self.service_interface.key)
        except Exception as e:
            raise GenAiException(e)
