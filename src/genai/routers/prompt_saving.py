from genai.exceptions import GenAiException
from genai.options import Options
from genai.schemas import PromptListParams
from genai.services import RequestHandler


class PromptSavingRouter:
    PROMPT_SAVING = "/prompts"

    def __init__(self, service_url: str, api_key: str) -> None:
        self.service_url = service_url.rstrip("/")
        self.key = api_key

    def list_prompts(self, params: PromptListParams = None):
        try:
            endpoint = self.service_url + PromptSavingRouter.PROMPT_SAVING
            return RequestHandler.get(endpoint, key=self.key, parameters=params)
        except Exception as e:
            raise GenAiException(e)

    def create_prompt(self, options=Options):
        try:
            endpoint = self.service_url + PromptSavingRouter.PROMPT_SAVING
            return RequestHandler.post(
                endpoint=endpoint,
                key=self.key,
                options=options,
            )
        except Exception as e:
            raise GenAiException(e)

    def update_prompt(self, id: str, options: Options):
        try:
            endpoint = self.service_url + PromptSavingRouter.PROMPT_SAVING + "/" + id
            return RequestHandler.put(
                endpoint,
                key=self.key,
                id=id,
                options=options,
            )
        except Exception as e:
            raise GenAiException(e)

    def get_prompt(self, id: str):
        if id is None:
            raise GenAiException("ID cannot be None when attempting to get a prompt.")
        try:
            endpoint = self.service_url + PromptSavingRouter.PROMPT_SAVING + "/" + id
            return RequestHandler.get(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def delete_prompt(self, id: str):
        if id is None:
            raise GenAiException("ID cannot be None when attempting to delete a prompt.")
        try:
            endpoint = self.service_url + PromptSavingRouter.PROMPT_SAVING + "/" + id
            return RequestHandler.delete(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)
