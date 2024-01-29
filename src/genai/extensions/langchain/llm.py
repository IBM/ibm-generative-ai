"""Wrapper around IBM GENAI APIs for use in Langchain"""

import asyncio
import logging
from functools import partial
from pathlib import Path
from typing import Any, Iterator, List, Optional, Union

from pydantic import ConfigDict
from pydantic.v1 import validator

from genai import Client
from genai._utils.general import to_model_instance, to_model_optional
from genai.extensions._common.utils import (
    _prepare_generation_request,
    create_generation_info,
    create_generation_info_from_response,
)
from genai.schema import (
    ModerationParameters,
    PromptTemplateData,
    TextGenerationParameters,
    TextGenerationStreamCreateResponse,
)
from genai.text.generation import CreateExecutionOptions

try:
    from langchain_core.callbacks.manager import (
        AsyncCallbackManagerForLLMRun,
        CallbackManagerForLLMRun,
    )
    from langchain_core.language_models.llms import LLM
    from langchain_core.messages import BaseMessage, get_buffer_string
    from langchain_core.outputs import LLMResult

    from genai.extensions.langchain.utils import (
        CustomGenerationChunk,
        create_llm_output,
        dump_optional_model,
        load_config,
        update_token_usage,
        update_token_usage_stream,
    )
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")  # noqa: B904

logger = logging.getLogger(__name__)

__all__ = ["LangChainInterface"]


class LangChainInterface(LLM):
    """
    Class representing the LangChainChatInterface for interacting with the LangChain chat API.

    Example::

        from genai import Client, Credentials
        from genai.extensions.langchain import LangChainInterface
        from genai.schema import TextGenerationParameters

        client = Client(credentials=Credentials.from_env())
        llm = LangChainInterface(
            client=client,
            model_id="meta-llama/llama-2-70b-chat",
            parameters=TextGenerationParameters(max_new_tokens=50)
        )

        response = chat_model.generate(prompts=["Hello world!"])
        print(response)
    """

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    client: Client
    model_id: str
    prompt_id: Optional[str] = None
    parameters: Optional[TextGenerationParameters] = None
    moderations: Optional[ModerationParameters] = None
    data: Optional[PromptTemplateData] = None
    streaming: Optional[bool] = None
    execution_options: Optional[CreateExecutionOptions] = None

    @validator("parameters", "moderations", "data", "execution_options", pre=True, always=True)
    @classmethod
    def _validate_data_models(cls, value, values, config, field):
        return to_model_optional(value, Model=field.type_, copy=False)

    @property
    def _common_identifying_params(self):
        return {
            "model_id": self.model_id,
            "prompt_id": self.prompt_id,
            "parameters": dump_optional_model(self.parameters),
            "moderations": dump_optional_model(self.moderations),
            "data": dump_optional_model(self.data),
            **super()._identifying_params,
        }

    @property
    def _identifying_stream_params(self) -> dict[str, Any]:
        return self._common_identifying_params

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {
            **self._common_identifying_params,
            "execution_options": dump_optional_model(self.execution_options),
        }

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
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "ibmgenai_llm"

    def _prepare_request(self, **kwargs):
        updated = {k: kwargs.pop(k, v) for k, v in self._identifying_params.items()}
        return _prepare_generation_request(**kwargs, **updated)

    def _prepare_stream_request(self, **kwargs):
        updated = {k: kwargs.pop(k, v) for k, v in self._identifying_stream_params.items()}
        return _prepare_generation_request(**kwargs, **updated)

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        result = self._generate(prompts=[prompt], stop=stop, run_manager=run_manager, **kwargs)
        return result.generations[0][0].text

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        final_result = LLMResult(generations=[], llm_output=create_llm_output(model=self.model_id))
        assert final_result.llm_output

        if len(prompts) == 0:
            return final_result

        if self.streaming:
            if len(prompts) != 1:
                raise ValueError("Streaming works only for a single prompt.")

            generation = CustomGenerationChunk(text="", generation_info=create_generation_info())

            for chunk_result in self._stream(
                prompt=prompts[0],
                stop=stop,
                run_manager=run_manager,
                **kwargs,
            ):
                assert chunk_result.generation_info
                token_usage = chunk_result.generation_info.pop("token_usage")
                generation += chunk_result
                assert generation.generation_info
                update_token_usage_stream(
                    target=generation.generation_info["token_usage"],
                    source=token_usage,
                )

            final_result.generations.append([generation])
            assert generation.generation_info
            update_token_usage(
                target=final_result.llm_output["token_usage"], source=generation.generation_info["token_usage"]
            )

            return final_result
        else:
            responses = list(
                self.client.text.generation.create(**self._prepare_request(inputs=prompts, stop=stop, **kwargs))
            )
            for response in responses:
                for result in response.results:
                    generation_info = create_generation_info_from_response(response, result=result)

                    chunk = CustomGenerationChunk(
                        text=result.generated_text or "",
                        generation_info=generation_info,
                    )
                    logger.info("Output of GENAI call: {}".format(chunk.text))
                    update_token_usage(
                        target=final_result.llm_output["token_usage"], source=generation_info["token_usage"]
                    )
                    final_result.generations.append([chunk])

            return final_result

    async def _agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        return await asyncio.get_running_loop().run_in_executor(
            None, partial(self._generate, prompts, stop, run_manager, **kwargs)
        )

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[CustomGenerationChunk]:
        params = to_model_instance(self.parameters, TextGenerationParameters)
        params.stop_sequences = stop or params.stop_sequences

        def send_chunk(
            *, text: Optional[str] = None, generation_info: dict, response: TextGenerationStreamCreateResponse
        ):
            logger.info("Chunk received: {}".format(text))
            chunk = CustomGenerationChunk(
                text=text or "",
                generation_info=generation_info.copy(),
            )
            yield chunk
            if run_manager:
                run_manager.on_llm_new_token(token=chunk.text, chunk=chunk, response=response)

        for response in self.client.text.generation.create_stream(
            **self._prepare_stream_request(input=prompt, stop=stop, **kwargs)
        ):
            if response.moderation:
                generation_info = create_generation_info_from_response(response, result=response.moderation)
                yield from send_chunk(generation_info=generation_info, response=response)

            for result in response.results or []:
                generation_info = create_generation_info_from_response(response, result=result)
                yield from send_chunk(text=result.generated_text, generation_info=generation_info, response=response)

    def get_num_tokens(self, text: str) -> int:
        response = list(self.client.text.tokenization.create(model_id=self.model_id, input=[text]))[0]
        return response.results[0].token_count

    def get_num_tokens_from_messages(self, messages: list[BaseMessage]) -> int:
        return sum(
            sum(result.token_count for result in response.results or [] if result.token_count)
            for response in self.client.text.tokenization.create(
                model_id=self.model_id, input=[get_buffer_string([message]) for message in messages]
            )
        )

    def get_token_ids(self, text: str) -> List[int]:
        raise NotImplementedError("API does not support returning token ids.")
