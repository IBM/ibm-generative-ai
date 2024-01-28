import asyncio
import logging
from functools import partial
from typing import Any, List, Optional, Sequence

from genai import Client
from genai._types import EnumLike
from genai.extensions._common.utils import (
    _prepare_chat_generation_request,
    create_generation_info_from_response,
)
from genai.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ModerationParameters,
    PromptTemplateData,
    SystemMessage,
    TextGenerationParameters,
    TrimMethod,
)

logger = logging.getLogger(__name__)


try:
    from llama_index.callbacks import CallbackManager
    from llama_index.llms.base import (
        ChatMessage,
        ChatResponse,
        ChatResponseAsyncGen,
        ChatResponseGen,
        CompletionResponse,
        CompletionResponseAsyncGen,
        CompletionResponseGen,
        LLMMetadata,
        llm_chat_callback,
        llm_completion_callback,
    )
    from llama_index.llms.llm import LLM
    from llama_index.llms.types import MessageRole


except ImportError:
    raise ImportError("Could not import llamaindex: Please install ibm-generative-ai[llama-index] extension.")  # noqa: B904


def to_genai_message(message: ChatMessage) -> BaseMessage:
    content = message.content or ""
    if message.role == MessageRole.USER:
        return HumanMessage(content=content)
    elif message.role == MessageRole.SYSTEM:
        return SystemMessage(content=content)
    elif message.role == MessageRole.ASSISTANT:
        return AIMessage(content=content)
    else:
        raise ValueError(f"Got unknown message type {message}")


def to_genai_messages(messages: Sequence[ChatMessage]) -> List[BaseMessage]:
    return [to_genai_message(msg) for msg in messages]


class IBMGenAILlamaIndex(LLM):
    client: Client

    # Generation related parameters
    model_id: str
    prompt_id: Optional[str] = None
    parameters: Optional[TextGenerationParameters] = None
    moderations: Optional[ModerationParameters] = None
    data: Optional[PromptTemplateData] = None

    # Chat (only) related parameters
    conversation_id: Optional[str] = None
    parent_id: Optional[str] = None
    prompt_template_id: Optional[str] = None
    trim_method: Optional[EnumLike[TrimMethod]] = None
    use_conversation_parameters: Optional[bool] = None

    def __init__(
        self, *, client: Client, model_id: str, callback_manager: Optional[CallbackManager] = None, **kwargs: Any
    ):
        super().__init__(
            client=client, callback_manager=callback_manager or CallbackManager(), model_id=model_id, **kwargs
        )

    @classmethod
    def class_name(cls) -> str:
        return "ibmgenai_llm"

    @property
    def _common_indentifying_params(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "prompt_id": self.prompt_id,
            "parameters": self.parameters,
            "moderations": self.moderations,
        }

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {
            **self._common_indentifying_params,
            "data": self.data,
        }

    @property
    def _identifying_chat_params(self) -> dict[str, Any]:
        return {
            **self._common_indentifying_params,
            "conversation_id": self.conversation_id,
            "parent_id": self.parent_id,
            "prompt_template_id": self.prompt_template_id,
            "trim_method": self.trim_method,
            "use_conversation_parameters": self.use_conversation_parameters,
        }

    def _prepare_request(self, source: dict[str, Any]):
        def prepare(**kwargs: Any):
            updated = {k: kwargs.pop(k, v) for k, v in source.items()}
            return _prepare_chat_generation_request(
                **kwargs,
                **updated,
            )

        return prepare

    @property
    def metadata(self) -> LLMMetadata:
        model = self.client.model.retrieve(self.model_id).result
        assert model.token_limits[0].token_limit
        context_window = int(model.token_limits[0].token_limit)
        return LLMMetadata(
            context_window=context_window,
            is_chat_model=True,
            is_function_calling_model=False,
            model_name=model.name or self.model_id,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:
        if not formatted:
            prompt = self.completion_to_prompt(prompt)

        response = list(
            self.client.text.generation.create(
                **self._prepare_request(self._identifying_params)(inputs=[prompt], **kwargs)
            )
        )[0]
        result = response.results[0]
        generation_info = create_generation_info_from_response(response, result=result)

        return CompletionResponse(text=result.generated_text or "", additional_kwargs=generation_info)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseGen:
        if not formatted:
            prompt = self.completion_to_prompt(prompt)

        text = ""
        for response in self.client.text.generation.create_stream(
            **self._prepare_request(self._identifying_params)(input=prompt, **kwargs)
        ):
            for result in response.results or []:
                generated_text = result.generated_text or ""
                generation_info = create_generation_info_from_response(response, result=result)

                text += generated_text
                yield CompletionResponse(text=text, delta=generated_text, additional_kwargs=generation_info)

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        genai_messages = to_genai_messages(messages)
        response = self.client.text.chat.create(
            **self._prepare_request(self._identifying_chat_params)(messages=genai_messages, **kwargs)
        )
        result = response.results[0]
        generation_info = create_generation_info_from_response(response, result=result)

        return ChatResponse(
            message=ChatMessage(
                role=MessageRole.ASSISTANT,
                content=result.generated_text or "",
            ),
            additional_kwargs=generation_info,
        )

    @llm_chat_callback()
    def stream_chat(self, messages: Sequence[ChatMessage], formatted: bool = False, **kwargs: Any) -> ChatResponseGen:
        text = ""

        for response in self.client.text.chat.create_stream(
            **self._prepare_request(self._identifying_chat_params)(messages=to_genai_messages(messages), **kwargs)
        ):
            if response.moderation:
                generation_info = create_generation_info_from_response(response, result=response.moderation)
                message = ChatMessage(role=MessageRole.ASSISTANT, content=text)
                yield ChatResponse(message=message, delta="", additional_kwargs=generation_info)

            for result in response.results or []:
                generated_text = result.generated_text or ""
                generation_info = create_generation_info_from_response(response, result=result)
                text += generated_text
                message = ChatMessage(role=MessageRole.ASSISTANT, content=text)
                yield ChatResponse(message=message, delta=generated_text, additional_kwargs=generation_info)

    @llm_completion_callback()
    async def acomplete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:
        return await asyncio.get_running_loop().run_in_executor(
            None, partial(self.complete, prompt, formatted, **kwargs)
        )

    @llm_completion_callback()
    async def astream_complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseAsyncGen:
        return await asyncio.get_running_loop().run_in_executor(
            None, partial(self.stream_complete, prompt, formatted, **kwargs)
        )

    @llm_chat_callback()
    async def achat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        return await asyncio.get_running_loop().run_in_executor(None, partial(self.chat, messages, **kwargs))

    @llm_chat_callback()
    async def astream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseAsyncGen:
        return await asyncio.get_running_loop().run_in_executor(None, partial(self.stream_chat, messages, **kwargs))
