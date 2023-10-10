import cachetools.func
from httpx import ConnectError, Response

from genai.exceptions import GenAiException
from genai.options import Options
from genai.routers import FilesRouter, PromptTemplateRouter, TunesRouter
from genai.schemas import GenerateParams, HistoryParams, TokenParams
from genai.schemas.responses import GenerateLimits
from genai.services.request_handler import RequestHandler
from genai.utils.errors import to_genai_error
from genai.utils.request_utils import sanitize_params

__all__ = ["ServiceInterface"]


class ServiceInterface:
    GENERATE = "/v1/generate"
    TOKENIZE = "/v1/tokenize"
    HISTORY = "/v1/requests"
    TOU = "/v1/user"
    MODELS = "/v1/models"
    GENERATE_LIMITS = "/v1/generate/limits"

    def __init__(self, service_url: str, api_key: str) -> None:
        """Initialize ServiceInterface.

        Args:
            service_url (str): Base URL for querying.
            api_key (str): User API key for authorization.
            use_async (bool): Use async version of methods
        """
        self.service_url = service_url.rstrip("/")
        self.key = api_key
        self._prompt_templating = PromptTemplateRouter(service_url=service_url, api_key=api_key)
        self._files = FilesRouter(service_url=service_url, api_key=api_key)
        self._tunes = TunesRouter(service_url=service_url, api_key=api_key)

    def models(self):
        """Generate a completion text for the given model, inputs, and params.

        Returns:
            Any: json from querying for text completion.
        """
        try:
            endpoint = self.service_url + ServiceInterface.MODELS
            return RequestHandler.get(endpoint, key=self.key)
        except ConnectError as e:
            raise GenAiException(
                Exception("Endpoint unreachable. Please check connectivity.\nRaw error message = {}".format(e))
            )
        except Exception as e:
            raise GenAiException(e)

    @cachetools.func.ttl_cache(ttl=1000, typed=True, maxsize=None)
    def generate_limits(self):
        """Retrieve generate limits for the account associated with current auth token."""
        try:
            endpoint = f"{self.service_url}{ServiceInterface.GENERATE_LIMITS}"
            response = RequestHandler.get(endpoint, key=self.key)
            if not response.is_success:
                raise GenAiException(response)
            return GenerateLimits(**response.json())
        except ConnectError as e:
            raise GenAiException("Endpoint unreachable. Please check connectivity.\nRaw error message = {}".format(e))
        except Exception as e:
            raise to_genai_error(e)

    def generate(
        self,
        model: str,
        inputs: list,
        params: GenerateParams = None,
        streaming: bool = False,
        options: Options = None,
    ):
        """Generate a completion text for the given model, inputs, and params.

        Args:
            model (str): Model id.
            inputs (list): List of inputs.
            params (GenerateParams, optional): Parameters for generation. Defaults to None.
            streaming (bool, optional): Streaming response flag. Defaults to False.
            options (Options, optional): Additional parameters to pass in the query payload. Defaults to None.

        Returns:
            Any: json from querying for text completion.
        """
        try:
            params = sanitize_params(params)
            endpoint = self.service_url + ServiceInterface.GENERATE
            res = RequestHandler.post(
                endpoint,
                key=self.key,
                model_id=model,
                inputs=inputs,
                parameters=params,
                streaming=streaming,
                options=options,
            )
            return res
        except Exception as e:
            raise GenAiException(e)

    def tokenize(
        self,
        model: str,
        inputs: list,
        params: TokenParams = None,
        options: Options = None,
    ):
        """Do the conversion of provided inputs to tokens for a given model.

        Args:
            model (str): Model id.
            inputs (list): List of inputs.
            params (TokenParams, optional): Parameters for generation. Defaults to None.

        Returns:
            Any: json from querying for tokenization.
        """
        try:
            params = sanitize_params(params)
            endpoint = self.service_url + ServiceInterface.TOKENIZE
            return RequestHandler.post(
                endpoint,
                key=self.key,
                model_id=model,
                inputs=inputs,
                parameters=params,
                options=options,
            )
        except Exception as e:
            raise GenAiException(e)

    def history(self, params: HistoryParams = None):
        """Retrieve past generation requests and responses returned by the given models.

        Args:
            params (HistoryParams, optional): Parameters for retrieving history. Defaults to None.

        Returns:
            Any: json from querying for tokenization.
        """
        try:
            params = sanitize_params(params)
            endpoint = self.service_url + ServiceInterface.HISTORY
            return RequestHandler.get(endpoint, key=self.key, parameters=params)
        except Exception as e:
            raise GenAiException(e)

    def terms_of_use(self, accept: bool) -> Response:
        """Accept the API Terms of Use

        Args:
            accept (bool): If the user accepts the TOU

        Raises:
            GenAiException: A general GenAI exception if there is an issue
                with the request

        Returns:
            httpx.Response: Response from REST API
        """
        tou_payload = {"tou_accepted": accept}

        try:
            endpoint = self.service_url + ServiceInterface.TOU
            return RequestHandler.patch(endpoint, key=self.key, json_data=tou_payload)
        except Exception as e:
            raise to_genai_error(e)

    # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
    #   ASYNC
    # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
    async def async_generate(self, model, inputs, params: GenerateParams = None, options: Options = None):
        """Generate a completion text for the given model, inputs, and params.

        Args:
            model (str): Model id.
            inputs (list): List of inputs.
            params (GenerateParams, optional): Parameters for generation. Defaults to None.

        Returns:
            Any: json from querying for text completion.
        """
        try:
            params = sanitize_params(params)
            endpoint = self.service_url + ServiceInterface.GENERATE
            return await RequestHandler.async_generate(
                endpoint,
                key=self.key,
                model_id=model,
                inputs=inputs,
                parameters=params,
                options=options,
            )
        except Exception as e:
            # without VPN this will fail
            raise GenAiException(e)

    async def async_tokenize(self, model, inputs, params: TokenParams = None, options: Options = None):
        """Do the conversion of provided inputs to tokens for a given model.

        Args:
            model (str): Model id.
            inputs (list): List of inputs.
            params (TokenParams, optional): Parameters for generation. Defaults to None.

        Returns:
            Any: json from querying for tokenization.
        """
        try:
            params = sanitize_params(params)
            endpoint = self.service_url + ServiceInterface.TOKENIZE
            return await RequestHandler.async_tokenize(
                endpoint,
                key=self.key,
                model_id=model,
                inputs=inputs,
                parameters=params,
                options=options,
            )
        except Exception as e:
            raise GenAiException(e)

    async def async_history(self, params: HistoryParams = None):
        """Retrieve past generation requests and responses returned by the given models.

        Args:
            params (HistoryParams, optional): Parameters for retrieving history. Defaults to None.

        Returns:
            Any: json from querying for tokenization.
        """
        try:
            params = sanitize_params(params)
            endpoint = self.service_url + ServiceInterface.HISTORY
            return await RequestHandler.async_get(endpoint, key=self.key, parameters=params)
        except Exception as e:
            raise GenAiException(e)

    async def async_terms_of_use(self, accept: bool) -> Response:
        """Accept the API Terms of Use

        Args:
            accept (bool): If the user accepts the TOU

        Raises:
            GenAiException: A general GenAI exception if there is an issue
                with the request

        Returns:
            httpx.Response: Response from REST API
        """
        tou_payload = {"tou_accepted": accept}

        try:
            endpoint = self.service_url + ServiceInterface.TOU
            return await RequestHandler.async_patch(endpoint, key=self.key, json_data=tou_payload)
        except Exception as e:
            raise GenAiException(e)
