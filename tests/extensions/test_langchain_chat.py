import json
from unittest.mock import MagicMock

import pytest
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain.schema.output import ChatGenerationChunk
from pytest_httpx import HTTPXMock, IteratorStream

from genai.extensions.langchain import LangChainChatInterface
from genai.extensions.langchain.utils import create_generation_info_from_response
from genai.schemas import GenerateParams
from genai.schemas.responses import ChatResponse, ChatStreamResponse
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint


@pytest.mark.extension
class TestLangChainChat:
    def setup_method(self):
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "meta-llama/llama-2-70b-chat"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def params(self):
        return GenerateParams()

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

    def test_generate(self, credentials, params, messages, httpx_mock: HTTPXMock):
        server_response = SimpleResponse.generate_chat(
            model_id=self.model,
            messages=messages,
            generated_text="Natural language processing (NLP) refers to the branch of computer science.",
        )
        expected_response = ChatResponse(**server_response)
        expected_result = expected_response.results[0]
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.CHAT), method="POST", json=server_response)

        chat_model = LangChainChatInterface(model=self.model, params=params, credentials=credentials)
        result = chat_model.generate(messages=[messages])
        assert len(result.generations) == 1
        assert len(result.generations[0]) == 1
        assert result.generations[0][0].text == expected_result.generated_text
        assert result.generations[0][0].generation_info == {
            "meta": {
                "id": expected_response.id,
                "created_at": expected_response.created_at,
                "conversation_id": expected_response.conversation_id,
            },
            "generated_token_count": expected_result.generated_token_count,
            "input_token_count": expected_result.input_token_count,
            "stop_reason": expected_result.stop_reason,
            "token_usage": {
                "prompt_tokens": expected_result.input_token_count,
                "completion_tokens": expected_result.generated_token_count,
                "total_tokens": expected_result.generated_token_count + (expected_result.input_token_count or 0),
                "generated_token_count": expected_result.generated_token_count,
                "input_token_count": expected_result.input_token_count,
            },
        }
        assert result.llm_output == {
            "model_name": self.model,
            "token_usage": {
                "prompt_tokens": expected_result.input_token_count,
                "completion_tokens": expected_result.generated_token_count,
                "total_tokens": expected_result.generated_token_count + (expected_result.input_token_count or 0),
                "generated_token_count": expected_result.generated_token_count,
                "input_token_count": expected_result.input_token_count,
            },
        }

    @pytest.mark.asyncio
    async def test_async_generate(self, credentials, params, messages, httpx_mock: HTTPXMock):
        server_response = SimpleResponse.generate_chat(
            model_id=self.model,
            messages=messages,
            generated_text="What is a molecule?",
        )
        expected_response = ChatResponse(**server_response)
        expected_result = expected_response.results[0]
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.CHAT), method="POST", json=server_response)
        chat_model = LangChainChatInterface(model=self.model, params=params, credentials=credentials)
        result = await chat_model.agenerate(messages=[messages])
        assert result.generations[0][0].text == expected_result.generated_text
        assert result.generations[0][0].generation_info
        assert result.llm_output

    def test_stream(self, credentials, params, messages, httpx_mock: HTTPXMock):
        server_response = SimpleResponse.generate_chat_stream(
            model_id=self.model,
            generated_text="What is a molecule?",
        )
        expected_generated_responses = [ChatStreamResponse(**result) for result in server_response]
        stream_responses = [f"data: {json.dumps(response)}\n\n".encode() for response in server_response]
        httpx_mock.add_response(
            url=match_endpoint(ServiceInterface.CHAT),
            stream=IteratorStream(stream_responses),
            headers={"Content-Type": "text/event-stream"},
        )

        callback = BaseCallbackHandler()
        callback.on_llm_new_token = MagicMock()

        model = LangChainChatInterface(
            model="google/flan-ul2",
            params=params,
            credentials=credentials,
            callbacks=[callback],
        )

        # Verify results
        for idx, result in enumerate(model.stream(input=messages)):
            assert isinstance(result, AIMessage)
            expected_response = expected_generated_responses[idx]
            assert (result.content or "") == (expected_response.results[0].generated_text or "")
            assert result.generation_info == create_generation_info_from_response(
                expected_response, result=expected_response.results[0]
            )

        # Verify that callbacks were called
        assert callback.on_llm_new_token.call_count == len(expected_generated_responses)
        for idx, result in enumerate(expected_generated_responses):
            retrieved_kwargs = callback.on_llm_new_token.call_args_list[idx].kwargs
            token = retrieved_kwargs["token"] or ""
            assert token == (result.results[0].generated_text or "")
            chunk = retrieved_kwargs["chunk"]
            assert isinstance(chunk, ChatGenerationChunk)
            response = retrieved_kwargs["response"]
            assert response == result
