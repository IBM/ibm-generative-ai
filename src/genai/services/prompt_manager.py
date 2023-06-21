import logging

from genai.credentials import Credentials
from genai.exceptions.genai_exception import GenAiException
from genai.schemas import GenerateParams, PromptListParams, PromptTemplateParams
from genai.schemas.responses import PromptListResponse, PromptResponse
from genai.services import ServiceInterface

logger = logging.getLogger(__name__)


class PromptManager:
    """Class for managing prompts on the server."""

    @staticmethod
    def list_prompts(creds: Credentials, params: PromptListParams = None):
        """List all prompts on the server.

        Args:
            credentials (Credentials): Credentials for the server.
            params (PromptListParams): Parameters for listing files.

        Returns:
            Any: Response from the server.
        """
        service = ServiceInterface(service_url=creds.api_endpoint, api_key=creds.api_key)
        try:
            response = service._prompt_saving.list_prompts(params=params)
            if response.status_code == 200:
                res = response.json()
                responses = PromptListResponse(**res)
                return responses
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def get_prompt(creds: Credentials, id: str):
        """Get a prompt from the server.

        Args:
            id (str): Prompt id.

        Returns:
            Any: Response from the server.
        """
        service = ServiceInterface(service_url=creds.api_endpoint, api_key=creds.api_key)
        try:
            response = service._prompt_saving.get_prompt(id=id)
            if response.status_code == 200:
                res = response.json()
                response = PromptResponse(**res["results"])
                return response
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def create_prompt(
        creds: Credentials,
        name: str,
        model_id: str,
        template: PromptTemplateParams,
        input: str = None,
        output: str = None,
        parameters: GenerateParams = None,
    ):
        """Create a prompt on the server.

        Args:
            credentials (Credentials): Credentials for the server.
            name (str): Name of the prompt.
            model_id (str): Model id.
            template (PromptTemplateParams): Template for the prompt.
            input (str, optional): Input for the prompt. Defaults to None.
            output (str, optional): Output for the prompt. Defaults to None.
            parameters (GenerateParams, optional): Parameters for the prompt. Defaults to None.

        Returns:
            Any: Response from the server.
        """
        service = ServiceInterface(service_url=creds.api_endpoint, api_key=creds.api_key)
        try:
            response = service._prompt_saving.create_prompt(
                name=name, model_id=model_id, template=template, input=input, output=output, parameters=parameters
            )
            if response.status_code == 200:
                response = response.json()
                return response
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def delete_prompt(creds: Credentials, id: str):
        """Delete a prompt from the server.

        Args:
            id (str): Prompt id.

        Returns:
            Any: Response from the server.
        """
        service = ServiceInterface(service_url=creds.api_endpoint, api_key=creds.api_key)
        try:
            response = service._prompt_saving.delete_prompt(id=id)
            if response.status_code == 204:
                return {"status": "success"}
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)
