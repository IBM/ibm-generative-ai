import asyncio
import logging
from functools import partial
from typing import Any, List, Optional, Sequence

from genai import Model
from genai.schemas.chat import (
    AIMessage,
    BaseMessage,
    ChatRole,
    HumanMessage,
    SystemMessage,
)
from genai.schemas.responses import ModelCard

logger = logging.getLogger(__name__)


try:
    from llama_index.callbacks import CallbackManager
    from llama_index.llms.base import (
        LLM,
        ChatMessage,
        ChatResponse,
        ChatResponseAsyncGen,
        ChatResponseGen,
        CompletionResponse,
        CompletionResponseAsyncGen,
        CompletionResponseGen,
        LLMMetadata,
        MessageRole,
        llm_chat_callback,
        llm_completion_callback,
    )

    class LlamaIndexChatMessageClasses:
        user = ChatMessage
        system = ChatMessage
        assistant = ChatMessage

except ImportError:
    raise ImportError("Could not import llamaindex: Please install ibm-generative-ai[llama-index] extension.")


def to_genai_message(message: ChatMessage) -> BaseMessage:
    if message.role == ChatRole.user:
        return HumanMessage(content=message.content)
    elif message.role == ChatRole.system:
        return SystemMessage(content=message.content)
    elif message.role == ChatRole.assistant:
        return AIMessage(content=message.content)
    else:
        raise ValueError(f"Got unknown message type {message}")


def to_genai_messages(messages: List[ChatMessage]) -> List[BaseMessage]:
    return [to_genai_message(msg) for msg in messages]


class IBMGenAILlamaIndex(LLM):
    model: Model
    model_info: Optional[ModelCard]

    def __init__(self, model: Model, callback_manager: Optional[CallbackManager] = None, **kwargs: Any):
        super().__init__(model=model, callback_manager=callback_manager, **kwargs)

        self.model_info = self.model.info()

    @classmethod
    def class_name(cls) -> str:
        "ibmgenai_llm"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.model_info.token_limit,
            is_chat_model=True,
            is_function_calling_model=False,
            model_name=self.model_info.name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        generation = self.model.generate(prompts=[prompt], **kwargs)[0]

        return CompletionResponse(text=generation.generated_text or "")

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        text = ""
        for response in self.model.generate_stream(prompts=[prompt], **kwargs):
            generated_text = response.generated_text or ""
            text += generated_text
            yield CompletionResponse(text=text, delta=generated_text)

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        genai_messages = to_genai_messages(messages)
        response = self.model.chat(messages=genai_messages, **kwargs)
        generated_text = response.results[0].generated_text or ""
        return ChatResponse(message=ChatMessage(role=MessageRole.ASSISTANT, content=generated_text))

    @llm_chat_callback()
    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseGen:
        genai_messages = to_genai_messages(messages)
        text = ""

        for response in self.model.chat_stream(messages=genai_messages, **kwargs):
            generated_text = response.results[0].generated_text or ""
            text += generated_text
            message = ChatMessage(role=ChatRole.assistant, content=text)
            yield ChatResponse(message=message, delta=generated_text)

    @llm_completion_callback()
    async def acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return await asyncio.get_running_loop().run_in_executor(None, partial(self.complete, prompt, **kwargs))

    @llm_completion_callback()
    async def astream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseAsyncGen:
        return await asyncio.get_running_loop().run_in_executor(None, partial(self.stream_complete, prompt, **kwargs))

    @llm_chat_callback()
    async def achat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        return await asyncio.get_running_loop().run_in_executor(None, partial(self.achat, messages, **kwargs))

    @llm_chat_callback()
    async def astream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseAsyncGen:
        return await asyncio.get_running_loop().run_in_executor(None, partial(self.stream_chat, messages, **kwargs))
