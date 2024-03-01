import pytest
from llama_index.core.llms import (
    ChatMessage,
    CompletionResponse,
    MessageRole,
)
from llama_index.core.llms import (
    ChatResponse as LlamaIndexChatResponse,
)

from genai.extensions._common.utils import create_generation_info_from_response
from genai.extensions.llama_index import IBMGenAILlamaIndex
from genai.schema import (
    TextChatCreateEndpoint,
    TextChatCreateResponse,
    TextChatStreamCreateEndpoint,
    TextGenerationCreateEndpoint,
    TextGenerationCreateResponse,
    TextGenerationStreamCreateEndpoint,
    TextGenerationStreamCreateResponse,
)


@pytest.mark.integration
class TestLlamaIndex:
    def setup_method(self):
        self.inputs = ["Write a tagline for an alumni association: Together we"]
        self.model_id = "google/flan-ul2"

    @pytest.fixture
    def llm(self, client):
        return IBMGenAILlamaIndex(client=client, model_id=self.model_id)

    @pytest.fixture
    def messages(self) -> list[ChatMessage]:
        return [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content="""You are a helpful, respectful and honest assistant.
    Always answer as helpfully as possible, while being safe.
    Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.
    Please ensure that your responses are socially unbiased and positive in nature. If a question does not make
    any sense, or is not factually coherent, explain why instead of answering something incorrectly.
    If you don't know the answer to a question, please don't share false information.
    """,
            ),
            ChatMessage(role=MessageRole.USER, content="What is NLP and how it has evolved over the years?"),
        ]

    @pytest.mark.vcr
    def test_llama_index_complete(self, llm, get_vcr_responses_of):
        prompt = "Hi! How's the weather, eh?"
        result = llm.complete(prompt)

        [raw_response] = get_vcr_responses_of(TextGenerationCreateEndpoint)
        api_response = TextGenerationCreateResponse.model_validate(raw_response)

        assert result.text == api_response.results[0].generated_text

        expected_result = api_response.results[0].model_dump()
        for key in {"stop_reason"}:
            assert result.additional_kwargs[key] == expected_result[key]

        assert result.additional_kwargs["token_usage"] == {
            "prompt_tokens": expected_result["input_token_count"],
            "completion_tokens": expected_result["generated_token_count"],
            "total_tokens": expected_result["input_token_count"] + expected_result["generated_token_count"],
        }

    @pytest.mark.vcr
    def test_llama_index_complete_stream(self, llm, get_vcr_responses_of):
        prompt = "Hi! How's the weather, eh?"
        llm_responses = list(llm.stream_complete(prompt))

        raw_responses = get_vcr_responses_of(TextGenerationStreamCreateEndpoint)
        api_responses = [TextGenerationStreamCreateResponse.model_validate(response) for response in raw_responses]

        expected_text = ""
        for idx, result in enumerate(llm_responses):
            expected_response = api_responses[idx]
            expected_delta = expected_response.results[0].generated_text
            expected_text += expected_delta
            assert isinstance(result, CompletionResponse) is True
            assert result.delta == expected_delta
            assert result.text == expected_text
            assert result.additional_kwargs == create_generation_info_from_response(
                expected_response, result=expected_response.results[0]
            )

    @pytest.mark.vcr
    def test_llama_index_chat(self, llm, messages, get_vcr_responses_of):
        result = llm.chat(messages=messages)

        [raw_response] = get_vcr_responses_of(TextChatCreateEndpoint)
        api_response = TextChatCreateResponse.model_validate(raw_response)

        assert isinstance(result, LlamaIndexChatResponse) is True
        assert result.message.content == api_response.results[0].generated_text
        assert result.additional_kwargs == create_generation_info_from_response(
            api_response, result=api_response.results[0]
        )

    @pytest.mark.vcr
    def test_llama_index_stream_chat(self, llm, messages, get_vcr_responses_of):
        llm_responses = list(llm.stream_chat(messages=messages))
        raw_responses = get_vcr_responses_of(TextChatStreamCreateEndpoint)
        api_responses = [TextGenerationStreamCreateResponse.model_validate(response) for response in raw_responses]
        expected_text = ""
        for idx, result in enumerate(llm_responses):
            expected_response = api_responses[idx]
            expected_delta = expected_response.results[0].generated_text or ""
            expected_text += expected_delta
            assert isinstance(result, LlamaIndexChatResponse) is True
            assert result.delta == expected_delta
            assert result.message.content == expected_text
            assert result.additional_kwargs == create_generation_info_from_response(
                expected_response, result=expected_response.results[0]
            )

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_async_llama_index_interface(self, llm, get_vcr_responses_of):
        prompt = "Hi! How's the weather, eh?"
        result = await llm.acomplete(prompt)

        [raw_response] = get_vcr_responses_of(TextGenerationCreateEndpoint)
        api_response = TextGenerationCreateResponse.model_validate(raw_response)

        assert isinstance(result, CompletionResponse)
        assert result.text == api_response.results[0].generated_text
