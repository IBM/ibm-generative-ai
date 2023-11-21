import asyncio
import logging
from functools import partial
from typing import Any, List, Optional, Sequence

from genai import Model
from genai.extensions.common.utils import create_generation_info_from_response
from genai.options import Options
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
    def complete(self, prompt: str, options: Optional[Options] = None) -> CompletionResponse:
        generation = self.model.generate(prompts=[prompt], options=options, raw_response=True)[0]
        result = generation.results[0]
        generation_info = create_generation_info_from_response(generation, result=result)

        return CompletionResponse(text=result.generated_text or "", additional_kwargs=generation_info)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, options: Optional[Options] = None) -> CompletionResponseGen:
        text = ""
        for response in self.model.generate_stream(prompts=[prompt], options=options, raw_response=True):
            result = response.results[0]
            generated_text = result.generated_text or ""
            generation_info = create_generation_info_from_response(response, result=result)

            text += generated_text
            yield CompletionResponse(text=text, delta=generated_text, additional_kwargs=generation_info)

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], options: Optional[Options] = None) -> ChatResponse:
        genai_messages = to_genai_messages(messages)
        response = self.model.chat(messages=genai_messages, options=options)
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
    def stream_chat(self, messages: Sequence[ChatMessage], options: Optional[Options] = None) -> ChatResponseGen:
        genai_messages = to_genai_messages(messages)
        text = ""

        for response in self.model.chat_stream(messages=genai_messages, options=options):
            result = response.results[0]
            generated_text = result.generated_text or ""
            generation_info = create_generation_info_from_response(response, result=result)

            text += generated_text
            message = ChatMessage(role=ChatRole.assistant, content=text)
            yield ChatResponse(message=message, delta=generated_text, additional_kwargs=generation_info)

    @llm_completion_callback()
    async def acomplete(self, prompt: str, options: Optional[Options] = None) -> CompletionResponse:
        return await asyncio.get_running_loop().run_in_executor(None, partial(self.complete, prompt, options=options))

    @llm_completion_callback()
    async def astream_complete(self, prompt: str, options: Optional[Options] = None) -> CompletionResponseAsyncGen:
        return await asyncio.get_running_loop().run_in_executor(
            None, partial(self.stream_complete, prompt, options=options)
        )

    @llm_chat_callback()
    async def achat(self, messages: Sequence[ChatMessage], options: Optional[Options] = None) -> ChatResponse:
        return await asyncio.get_running_loop().run_in_executor(None, partial(self.chat, messages, options=options))

    @llm_chat_callback()
    async def astream_chat(
        self, messages: Sequence[ChatMessage], options: Optional[Options] = None
    ) -> ChatResponseAsyncGen:
        return await asyncio.get_running_loop().run_in_executor(
            None, partial(self.stream_chat, messages, options=options)
        )
