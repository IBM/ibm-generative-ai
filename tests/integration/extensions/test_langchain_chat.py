from unittest.mock import MagicMock

import pytest
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGenerationChunk

from genai.extensions._common.utils import create_generation_info_from_response
from genai.extensions.langchain import LangChainChatInterface
from genai.schema import (
    TextChatCreateEndpoint,
    TextChatCreateResponse,
    TextChatStreamCreateResponse,
    TextGenerationParameters,
)


@pytest.mark.integration
class TestLangChainChat:
    def setup_method(self):
        self.model_id = "meta-llama/llama-3-1-70b-instruct"

    @pytest.fixture
    def parameters(self):
        return TextGenerationParameters()

    @pytest.fixture
    def messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(
                content="""You are a helpful, respectful and honest assistant.
    Always answer as helpfully as possible, while being safe.
    Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.
    Please ensure that your responses are socially unbiased and positive in nature. If a question does not make
    any sense, or is not factually coherent, explain why instead of answering something incorrectly.
    If you don't know the answer to a question, please don't share false information.
    """,
            ),
            HumanMessage(content="What is NLP and how it has evolved over the years?"),
        ]

    @pytest.mark.vcr
    def test_generate(self, client, parameters, messages, get_vcr_responses_of):
        chat_model = LangChainChatInterface(model_id=self.model_id, parameters=parameters, client=client)
        result = chat_model.generate(messages=[messages])

        [server_response] = get_vcr_responses_of(TextChatCreateEndpoint)
        expected_response = TextChatCreateResponse(**server_response)

        assert len(result.generations) == 1
        assert len(result.generations[0]) == 1
        [expected_result] = expected_response.results
        assert result.generations[0][0].text == expected_result.generated_text
        assert result.generations[0][0].generation_info == {
            "meta": {
                "id": expected_response.id,
                "created_at": expected_response.created_at,
                "conversation_id": expected_response.conversation_id,
                "model_id": expected_response.model_id,
            },
            "generated_token_count": expected_result.generated_token_count,
            "input_token_count": expected_result.input_token_count,
            "stop_reason": expected_result.stop_reason,
            "seed": expected_result.seed,
            "token_usage": {
                "prompt_tokens": expected_result.input_token_count,
                "completion_tokens": expected_result.generated_token_count,
                "total_tokens": expected_result.generated_token_count + (expected_result.input_token_count or 0),
            },
        }
        assert result.llm_output == {
            "model_name": self.model_id,
            "token_usage": {
                "prompt_tokens": expected_result.input_token_count,
                "completion_tokens": expected_result.generated_token_count,
                "total_tokens": expected_result.generated_token_count + (expected_result.input_token_count or 0),
            },
        }

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_async_generate(self, client, parameters, messages, get_vcr_responses_of):
        chat_model = LangChainChatInterface(model_id=self.model_id, parameters=parameters, client=client)
        result = await chat_model.agenerate(messages=[messages])

        [raw_response] = get_vcr_responses_of(TextChatCreateEndpoint)
        api_response = TextChatCreateResponse.model_validate(raw_response)
        expected_result = api_response.results[0]

        assert result.generations[0][0].text == expected_result.generated_text
        assert result.generations[0][0].generation_info
        assert result.llm_output

    @pytest.mark.vcr
    def test_stream(self, client, parameters, messages, get_vcr_responses_of):
        callback = BaseCallbackHandler()
        callback.on_llm_new_token = MagicMock()

        model = LangChainChatInterface(
            model_id="google/flan-ul2", parameters=parameters, callbacks=[callback], client=client
        )
        model_responses = list(model.stream(input=messages))

        raw_responses = get_vcr_responses_of(TextChatCreateEndpoint)
        api_responses = [TextChatStreamCreateResponse.model_validate(response) for response in raw_responses]

        # Verify results
        for idx, result in enumerate(model_responses):
            assert isinstance(result, AIMessage)
            expected_response = api_responses[idx]
            assert (result.content or "") == (expected_response.results[0].generated_text or "")
            assert result.generation_info == create_generation_info_from_response(
                expected_response, result=expected_response.results[0]
            )

        # Verify that callbacks were called
        assert callback.on_llm_new_token.call_count == len(api_responses)
        for idx, result in enumerate(api_responses):
            retrieved_kwargs = callback.on_llm_new_token.call_args_list[idx].kwargs
            token = retrieved_kwargs["token"] or ""
            assert token == (result.results[0].generated_text or "")
            chunk = retrieved_kwargs["chunk"]
            assert isinstance(chunk, ChatGenerationChunk)
