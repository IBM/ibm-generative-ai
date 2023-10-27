
from langchain.llms.base import create_base_retry_decorator
from langchain.schema import ChatGeneration, ChatResult
from langchain.schema.messages import (
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessageChunk,
    FunctionMessageChunk,
    HumanMessageChunk,
    SystemMessageChunk,
)

from langchain.adapters.openai import convert_dict_to_message, convert_message_to_dict
from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)

import logging

from langchain.pydantic_v1 import Field, root_validator
from langchain.chat_models.base import BaseChatModel
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)


from genai.extensions.langchain.bam import BAM

logger = logging.getLogger(__name__)

__all__ = ["WatsonX"]


class WatsonX(BaseChatModel):

    @property
    def lc_secrets(self) -> Dict[str, str]:

        return {"watsonx_api_key": "GENAI_KEY"}

    @property
    def lc_attributes(self) -> Dict[str, Any]:
        attributes: Dict[str, Any] = {}

        if self.watsonx_organization != "":
            attributes["watsonx_organization"] = self.watsonx_organization

        if self.watsonx_api_base != "":
            attributes["watsonx_api_base"] = self.watsonx_api_base

        if self.watsonx_proxy != "":
            attributes["watsonx_proxy"] = self.watsonx_proxy

        return attributes

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this model can be serialized by Langchain."""
        return False

    client: Any = None  #: :meta private:
    model_name: str = Field(default="ibm/falcon-40b-8lang-instruct", alias="model")
    """Model name to use."""
    temperature: float = 0.7
    """What sampling temperature to use."""
    model_kwargs: Dict[str, Any] = None
    """Number of chat completions to generate for each prompt."""
    watsonx_api_key: str = None
    watsonx_api_base: str = None
    watsonx_organization: str = "ibm"
    
    # openai_api_key: Optional[str] = None
    # """Base URL path for API requests, 
    # leave blank if not using a proxy or service emulator."""
    # openai_api_base: Optional[str] = None
    # openai_organization: Optional[str] = None

    # # to support explicit proxy for OpenAI
    # openai_proxy: Optional[str] = None
    max_tokens: Optional[int] = None
    """Maximum number of tokens to generate."""
    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    """Timeout for requests to OpenAI completion API. Default is 600 seconds."""
    max_retries: int = 6
    """Maximum number of retries to make when generating."""
    streaming: bool = False
    """Whether to stream the results or not."""
    n: int = 1
    """Number of chat completions to generate for each prompt."""

    tiktoken_model_name: Optional[str] = None
    """The model name to pass to tiktoken when using this class. 
    Tiktoken is used to count the number of tokens in documents to constrain 
    them to be under a certain limit. By default, when set to None, this will 
    be the same as the embedding model name. However, there are some cases 
    where you may want to use this Embedding class with a model name not 
    supported by tiktoken. This can include when using Azure embeddings or 
    when using one of the many model providers that expose an OpenAI-like 
    API but with different models. In those cases, in order to avoid erroring 
    when tiktoken is called, you can specify a model name to use here."""

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True


    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        return {
            "model": self.model_name,
            "request_timeout": self.request_timeout,
            "max_tokens": self.max_tokens,
            "stream": self.streaming,
            "n": self.n,
            "temperature": self.temperature,
            **self.model_kwargs,
        }


    def completion_with_retry(
        self, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any
    ) -> Any:
        """Use tenacity to retry the completion call."""
        retry_decorator = _create_retry_decorator(self, run_manager=run_manager)


        # print(f'In - completion_with_retry - kwargs = {kwargs}')
        self.client = BAM(
            model_name=self.model_name, 
            watsonx_api_key=self.watsonx_api_key, 
            watsonx_api_base=self.watsonx_api_base, 
            model_kwargs=self.model_kwargs
            )

        @retry_decorator
        def _completion_with_retry(**kwargs: Any) -> Any:
            return self.client.create(**kwargs)

        return _completion_with_retry(**kwargs)

    def _combine_llm_outputs(self, llm_outputs: List[Optional[dict]]) -> dict:
        overall_token_usage: dict = {}
        for output in llm_outputs:
            if output is None:
                # Happens in streaming
                continue
            token_usage = output["token_usage"]
            for k, v in token_usage.items():
                if k in overall_token_usage:
                    overall_token_usage[k] += v
                else:
                    overall_token_usage[k] = v
        return {"token_usage": overall_token_usage, "model_name": self.model_name}

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # should_stream = stream if stream is not None else self.streaming
        # if should_stream:
        #     stream_iter = self._stream(
        #         messages, stop=stop, run_manager=run_manager, **kwargs
        #     )
        #     return _generate_from_stream(stream_iter)
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        response = self.completion_with_retry(
            messages=message_dicts, run_manager=run_manager, **params
        )

        logging.info(f'response = {response}')
        return self._create_chat_result(response)
    
    def _create_chat_result(self, response: Mapping[str, Any]) -> ChatResult:
        generations = []
        for res in response["choices"]:
            message = convert_dict_to_message(res["message"])
            gen = ChatGeneration(
                message=message,
                generation_info=dict(finish_reason=res.get("finish_reason")),
            )
            generations.append(gen)
        token_usage = response.get("usage", {})
        llm_output = {"token_usage": token_usage, "model_name": self.model_name}
        return ChatResult(generations=generations, llm_output=llm_output)

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "openai-chat"

    def _create_message_dicts(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        params = self._client_params
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params["stop"] = stop
        message_dicts = [convert_message_to_dict(m) for m in messages]
        return message_dicts, params

    @property
    def _client_params(self) -> Dict[str, Any]:
        """Get the parameters used for the openai client."""
        # openai_creds: Dict[str, Any] = {
        #     "watsonx_api_key": self.openai_api_key,
        #     "api_base": self.openai_api_base,
        #     "organization": self.openai_organization,
        #     "model": self.model_name,
        # }

        watsonx_creds: Dict[str, Any] = {
            "watsonx_api_key": self.watsonx_api_key,
            "watsonx_api_base": self.watsonx_api_base,
            "organization": self.watsonx_organization,
            "model": self.model_name,
        }
        # if self.openai_proxy:
        #     import openai

        #     openai.proxy = {"http": self.openai_proxy, "https": self.openai_proxy}  # type: ignore[assignment]  # noqa: E501

        return {**self._default_params, **watsonx_creds}

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {**{"model_name": self.model_name}, **self._default_params}


def _create_retry_decorator(
    llm: WatsonX,
    run_manager: Optional[
        Union[AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun]
    ] = None,
) -> Callable[[Any], Any]:
    import openai
    errors = [
        openai.error.Timeout,
        openai.error.APIError,
        openai.error.APIConnectionError,
        openai.error.RateLimitError,
        openai.error.ServiceUnavailableError,
    ]
    return create_base_retry_decorator(
        error_types=errors, max_retries=llm.max_retries, run_manager=run_manager
)