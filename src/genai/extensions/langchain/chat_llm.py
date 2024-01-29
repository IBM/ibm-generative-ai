"""Wrapper around IBM GENAI APIs for use in Langchain"""

import logging
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union

from pydantic import ConfigDict
from pydantic.v1 import validator

from genai import Client
from genai._types import EnumLike
from genai._utils.general import to_model_optional
from genai.extensions._common.utils import (
    _prepare_chat_generation_request,
    create_generation_info_from_response,
)
from genai.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ModerationParameters,
    SystemMessage,
    TextGenerationParameters,
    TrimMethod,
)

try:
    from langchain_core.callbacks.manager import CallbackManagerForLLMRun
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage as LCAIMessage
    from langchain_core.messages import AIMessageChunk as LCAIMessageChunk
    from langchain_core.messages import BaseMessage as LCBaseMessage
    from langchain_core.messages import ChatMessage as LCChatMessage
    from langchain_core.messages import HumanMessage as LCHumanMessage
    from langchain_core.messages import SystemMessage as LCSystemMessage
    from langchain_core.messages import get_buffer_string
    from langchain_core.outputs import ChatGeneration, ChatResult

    from genai.extensions.langchain.utils import (
        CustomChatGenerationChunk,
        create_llm_output,
        dump_optional_model,
        load_config,
        update_token_usage_stream,
    )
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")  # noqa: B904

__all__ = ["LangChainChatInterface"]

logger = logging.getLogger(__name__)

Message = Union[LCBaseMessage, BaseMessage]
Messages = Union[list[LCBaseMessage], list[Message]]


def _convert_message_to_genai(message: Message) -> BaseMessage:
    def convert_message_content(content: Any) -> str:
        if not isinstance(content, str):
            raise TypeError(
                f"Cannot convert non-string message content. Got {content} of type {type(content)}, expected string."
            )

        return content

    if isinstance(message, BaseMessage):
        return message
    elif isinstance(message, LCChatMessage) or isinstance(message, LCHumanMessage):
        return HumanMessage(content=convert_message_content(message.content))
    elif isinstance(message, LCAIMessage):
        return AIMessage(content=convert_message_content(message.content))
    elif isinstance(message, LCSystemMessage):
        return SystemMessage(content=convert_message_content(message.content))
    else:
        raise ValueError(f"Got unknown message type '{message}'")


def _convert_messages_to_genai(messages: Messages) -> list[BaseMessage]:
    return [_convert_message_to_genai(msg) for msg in messages]


class LangChainChatInterface(BaseChatModel):
    """
    Class representing the LangChainChatInterface for interacting with the LangChain chat API.

    Example::

        from genai import Client, Credentials
        from genai.extensions.langchain import LangChainChatInterface
        from langchain_core.messages import HumanMessage, SystemMessage
        from genai.schema import TextGenerationParameters

        client = Client(credentials=Credentials.from_env())
        llm = LangChainChatInterface(
            client=client,
            model_id="meta-llama/llama-2-70b-chat",
            parameters=TextGenerationParameters(
                max_new_tokens=250,
            )
        )

        response = chat_model.generate(messages=[HumanMessage(content="Hello world!")])
        print(response)

    """

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    client: Client
    model_id: str
    prompt_id: Optional[str] = None
    parameters: Optional[TextGenerationParameters] = None
    moderations: Optional[ModerationParameters] = None
    parent_id: Optional[str] = None
    prompt_template_id: Optional[str] = None
    trim_method: Optional[EnumLike[TrimMethod]] = None
    use_conversation_parameters: Optional[bool] = None
    conversation_id: Optional[str] = None
    streaming: Optional[bool] = None

    @validator("parameters", "moderations", pre=True, always=True)
    @classmethod
    def validate_data_models(cls, value, values, config, field):
        return to_model_optional(value, Model=field.type_, copy=False)

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"client": "CLIENT"}

    @classmethod
    def load_from_file(cls, file: Union[str, Path], *, client: Client):
        config = load_config(file)
        return cls(**config, client=client)

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "prompt_id": self.prompt_id,
            "parameters": dump_optional_model(self.parameters),
            "moderations": dump_optional_model(self.moderations),
            "parent_id": self.parent_id,
            "prompt_template_id": self.prompt_template_id,
            "trim_method": self.trim_method,
            "use_conversation_parameters": self.use_conversation_parameters,
            **super()._identifying_params,
        }

    @property
    def _llm_type(self) -> str:
        return "ibmgenai_chat_llm"

    def _prepare_request(self, **kwargs):
        updated = {k: kwargs.pop(k, v) for k, v in self._identifying_params.items()}
        return _prepare_chat_generation_request(**kwargs, **updated)

    def _stream(
        self,
        messages: Messages,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[CustomChatGenerationChunk]:
        for response in self.client.text.chat.create_stream(
            **self._prepare_request(messages=_convert_messages_to_genai(messages), stop=stop, **kwargs)
        ):
            if not response:
                continue

            def send_chunk(*, text: str = "", generation_info: dict):
                logger.info("Chunk received: {}".format(text))
                chunk = CustomChatGenerationChunk(
                    message=LCAIMessageChunk(content=text, generation_info=generation_info),
                    generation_info=generation_info,
                )
                yield chunk
                if run_manager:
                    run_manager.on_llm_new_token(token=text, chunk=chunk, response=response)  # noqa: B023
                    # Function definition does not bind loop variable `response`: linter is probably just confused here

            if response.moderation:
                generation_info = create_generation_info_from_response(response, result=response.moderation)
                yield from send_chunk(generation_info=generation_info)

            for result in response.results or []:
                generation_info = create_generation_info_from_response(response, result=result)
                yield from send_chunk(text=result.generated_text or "", generation_info=generation_info)

    def _generate(
        self,
        messages: Messages,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        def handle_stream():
            final_generation: Optional[CustomChatGenerationChunk] = None
            for result in self._stream(
                messages=messages,
                stop=stop,
                run_manager=run_manager,
                **kwargs,
            ):
                if final_generation:
                    token_usage = result.generation_info.pop("token_usage")
                    final_generation += result
                    update_token_usage_stream(
                        target=final_generation.generation_info["token_usage"],
                        source=token_usage,
                    )
                else:
                    final_generation = result

            assert final_generation and final_generation.generation_info
            return {
                "text": final_generation.text,
                "generation_info": final_generation.generation_info.copy(),
            }

        def handle_non_stream():
            response = self.client.text.chat.create(
                **self._prepare_request(messages=_convert_messages_to_genai(messages), stop=stop, **kwargs),
            )

            assert response.results
            result = response.results[0]

            return {
                "text": result.generated_text or "",
                "generation_info": create_generation_info_from_response(response, result=result),
            }

        result = handle_stream() if self.streaming else handle_non_stream()
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=LCAIMessage(content=result["text"]),
                    generation_info=result["generation_info"].copy(),
                )
            ],
            llm_output=create_llm_output(
                model=result["generation_info"].get("model_id", self.model_id or ""),
                token_usages=[result["generation_info"]["token_usage"]],
            ),
        )

    def get_num_tokens(self, text: str) -> int:
        response = list(self.client.text.tokenization.create(model_id=self.model_id, input=[text]))[0]
        return response.results[0].token_count

    def get_num_tokens_from_messages(self, messages: list[LCBaseMessage]) -> int:
        return sum(
            sum(result.token_count for result in response.results)
            for response in self.client.text.tokenization.create(
                model_id=self.model_id, input=[get_buffer_string([message]) for message in messages]
            )
        )

    def _combine_llm_outputs(self, llm_outputs: list[Optional[dict]]) -> dict:
        token_usages: list[Optional[dict]] = []
        model = ""

        for output in llm_outputs:
            if output:
                model = model or output.get("meta", {}).get("model_id")
                token_usages.append(output.get("token_usage"))

        return create_llm_output(model=model or self.model_id, token_usages=token_usages)

    def get_token_ids(self, text: str) -> list[int]:
        raise NotImplementedError("API does not support returning token ids.")
