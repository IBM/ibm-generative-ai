import logging

from genai.credentials import Credentials
from genai.exceptions.genai_exception import GenAiException
from genai.options import Options
from genai.schemas import GenerateParams, PromptListParams
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
        model_id: str = None,
        prompt_prototype: dict = None,
        input: str = None,
        output: str = None,
        generate_params: GenerateParams = None,
    ):
        """Create a prompt on the server.

        Args:
            credentials (Credentials): Credentials for the server.
            name (str): Name of the prompt.
            model_id (str): Model id.
            prompt_prototype (dict): Structure design for the prompt. Accepts a dictionary with the
                following keys: watsonx_template_id, watsonx_template_value, and prompt_data with the data used
                to populate your prompt.
            input (str, optional): Input for the prompt. Defaults to None.
            output (str, optional): Output for the prompt. Defaults to None.
            parameters (GenerateParams, optional): Parameters for the prompt. Defaults to None.

        Returns:
            Any: Response from the server.
        """
        # NOTE: There's is particular reason to require model_id? Since we can pass it in the generate parameters,
        # and we can reuse a prompt with different models, I think it's better to not require it.

        prompt_prototype = PromptManager._rewrite_prompt_prototype(prompt_prototype)

        service = ServiceInterface(service_url=creds.api_endpoint, api_key=creds.api_key)

        options = Options(
            name=name,
            model_id=model_id,
            template=prompt_prototype,
            input=input,
            output=output,
            parameters=generate_params,
        )

        # NOTE: input here, when creating a prompt need to be a single string, not a list of strings
        # but if the input is a list of strings, need to be passed as prompt in the generate parameters
        try:
            response = service._prompt_saving.create_prompt(options=options)
            if response.status_code == 200:
                res = response.json()
                response = PromptResponse(**res["results"])
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

    @staticmethod
    def _rewrite_prompt_prototype(prompt_prototype: dict):
        """Rewrite the prompt prototype to match the server's expectations.

        Args:
            prompt_prototype (dict): Prompt prototype.

        Returns:
            dict: Prompt prototype.
        """
        if prompt_prototype:
            prompt_prototype["id"] = prompt_prototype.pop("watsonx_template_id", None)
            prompt_prototype["value"] = prompt_prototype.pop("watsonx_template_value", None)
            prompt_prototype["data"] = prompt_prototype.pop("prompt_data", None)
        return prompt_prototype
