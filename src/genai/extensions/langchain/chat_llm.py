"""Wrapper around IBM GENAI APIs for use in Langchain"""
import logging
from typing import Any, Dict, Iterator, Optional, Union

from pydantic import ConfigDict

from genai import Credentials, Model
from genai.exceptions import GenAiException
from genai.extensions.langchain.utils import (
    create_generation_info_from_response,
    create_llm_output,
    extract_token_usage,
    update_token_usage,
)
from genai.schemas import GenerateParams
from genai.schemas.chat import AIMessage, BaseMessage, HumanMessage, SystemMessage
from genai.schemas.generate_params import ChatOptions
from genai.utils.general import to_model_instance

try:
    from langchain.callbacks.manager import CallbackManagerForLLMRun
    from langchain.chat_models.base import BaseChatModel
    from langchain.schema.messages import AIMessage as LCAIMessage
    from langchain.schema.messages import AIMessageChunk as LCAIMessageChunk
    from langchain.schema.messages import BaseMessage as LCBaseMessage
    from langchain.schema.messages import ChatMessage as LCChatMessage
    from langchain.schema.messages import HumanMessage as LCHumanMessage
    from langchain.schema.messages import SystemMessage as LCSystemMessage
    from langchain.schema.messages import get_buffer_string
    from langchain.schema.output import ChatGeneration, ChatGenerationChunk, ChatResult
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")

__all__ = ["LangChainChatInterface"]


logger = logging.getLogger(__name__)

Message = Union[LCBaseMessage, BaseMessage]
Messages = Union[list[LCBaseMessage], list[Message]]


def convert_message_to_genai(message: Message) -> BaseMessage:
    if isinstance(message, BaseMessage):
        return message
    elif isinstance(message, LCChatMessage) or isinstance(message, LCHumanMessage):
        return HumanMessage(content=message.content)
    elif isinstance(message, LCAIMessage):
        return AIMessage(content=message.content)
    elif isinstance(message, LCSystemMessage):
        return SystemMessage(content=message.content)
    else:
        raise ValueError(f"Got unknown message type {message}")


def convert_messages_to_genai(messages: Messages) -> list[BaseMessage]:
    return [convert_message_to_genai(msg) for msg in messages]


class LangChainChatInterface(BaseChatModel):
    """
    Wrapper around IBM GENAI models.
    To use, you should have the ``genai`` python package installed
    and initialize the credentials attribute of this class with
    an instance of ``genai.Credentials``. Model specific parameters
    can be passed through to the constructor using the ``params``
    parameter, which is an instance of GenerateParams.
    Example:
        .. code-block:: python
            llm = ChatGenAI(model="meta-llama/llama-2-70b-chat", credentials=creds)
    """

    credentials: Credentials
    model: str
    params: Optional[GenerateParams] = None
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    @property
    def _llm_type(self) -> str:
        return "Chat IBM GENAI"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        _params = to_model_instance(self.params, GenerateParams)
        return {
            **{"model": self.model},
            **{"params": _params},
        }

    class Config:
        """Configuration for this pydantic object."""

        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    def _stream(
        self,
        messages: Messages,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        *,
        options: Optional[ChatOptions] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        params = to_model_instance(self.params, GenerateParams)
        params.stop_sequences = stop or params.stop_sequences
        model = Model(self.model, params=params, credentials=self.credentials)

        stream = model.chat_stream(messages=convert_messages_to_genai(messages), options=options, **kwargs)
        for response in stream:
            result = response.results[0] if response else None
            if not result:
                continue

            generated_text = result.generated_text or ""
            generation_info = create_generation_info_from_response(response)
            chunk = ChatGenerationChunk(
                message=LCAIMessageChunk(content=generated_text, generation_info=generation_info),
                generation_info=generation_info,
            )
            yield chunk
            if run_manager:
                run_manager.on_llm_new_token(token=generated_text, chunk=chunk, response=response)

    def _generate(
        self,
        messages: Messages,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        *,
        options: Optional[ChatOptions] = None,
        **kwargs: Any,
    ) -> ChatResult:
        params = to_model_instance(self.params, GenerateParams)
        params.stop_sequences = stop or params.stop_sequences

        model = Model(self.model, params=params, credentials=self.credentials)
        response = model.chat(messages=convert_messages_to_genai(messages), options=options, **kwargs)
        result = response.results[0]
        assert result

        message = LCAIMessage(content=result.generated_text or "")
        return ChatResult(
            generations=[
                ChatGeneration(message=message, generation_info=create_generation_info_from_response(response))
            ],
            llm_output=create_llm_output(
                model=self.model,
                token_usage=extract_token_usage(result.model_dump()),
            ),
        )

    def get_num_tokens(self, text: str) -> int:
        model = Model(self.model, params=self.params, credentials=self.credentials)
        response = model.tokenize([text], return_tokens=False)[0]
        if response.token_count is None:
            raise GenAiException("Invalid tokenize result!")
        return response.token_count

    def get_num_tokens_from_messages(self, messages: list[LCBaseMessage]) -> int:
        model = Model(self.model, params=self.params, credentials=self.credentials)
        responses = model.tokenize([get_buffer_string([message]) for message in messages], return_tokens=False)
        return sum([response.token_count for response in responses if response.token_count])

    def _combine_llm_outputs(self, llm_outputs: list[Optional[dict]]) -> dict:
        overall_token_usage: dict = extract_token_usage({})
        update_token_usage(
            target=overall_token_usage, sources=[output.get("token_usage") for output in llm_outputs if output]
        )
        return {"model_name": self.model, "token_usage": overall_token_usage}
