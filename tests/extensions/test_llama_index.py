import json

import pytest
from pytest_httpx import HTTPXMock, IteratorStream

from genai import Credentials, Model
from genai.extensions.llama_index import IBMGenAILlamaIndex
from genai.schemas import GenerateParams
from genai.schemas.api_responses import ApiGenerateStreamResponse
from genai.schemas.chat import BaseMessage
from genai.schemas.responses import ChatResponse, ChatStreamResponse, GenerateResponse
from genai.services import ServiceInterface
from src.genai.extensions.common.utils import create_generation_info_from_response
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint

try:
    from llama_index.llms.base import ChatMessage
    from llama_index.llms.base import ChatResponse as LlamaIndexChatResponse
    from llama_index.llms.base import CompletionResponse, MessageRole

except ImportError:
    raise ImportError("Could not import llamaindex: Please install ibm-generative-ai[llama-index] extension.")


@pytest.mark.extension
class TestLlamaIndex:
    def setup_method(self):
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.inputs = ["Write a tagline for an alumni association: Together we"]
        self.model = "google/flan-ul2"

    @pytest.fixture
    def llm(self, httpx_mock: HTTPXMock):
        models_info_response = SimpleResponse.models()
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.MODELS), method="GET", json=models_info_response)

        return IBMGenAILlamaIndex(
            model=Model(self.model, credentials=Credentials(api_key="API_KEY"), params=GenerateParams())
        )

    @pytest.fixture
    def params(self):
        return GenerateParams()

    @pytest.fixture
    def prompts(self):
        return ["Hi! How's the weather, eh?"]

    @pytest.fixture
    def messages(self) -> list[BaseMessage]:
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

    def test_llama_index_complete(self, llm, params, prompts, httpx_mock: HTTPXMock):
        generate_response = SimpleResponse.generate(model=self.model, inputs=prompts, params=params)
        expected_response = GenerateResponse(**generate_response)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=generate_response)
        result = llm.complete(prompts[0])
        assert result.text == expected_response.results[0].generated_text

        expected_result = expected_response.results[0].model_dump()
        for key in {"input_text", "stop_reason"}:
            assert result.additional_kwargs[key] == expected_result[key]
        for key in {"input_token_count", "generated_token_count"}:
            assert result.additional_kwargs["token_usage"][key] == expected_result[key]

    def test_llama_index_complete_stream(self, llm, params, prompts, httpx_mock: HTTPXMock):
        generate_stream_responses = SimpleResponse.generate_stream(model=self.model, inputs=prompts, params=params)
        expected_generated_responses = [ApiGenerateStreamResponse(**result) for result in generate_stream_responses]
        stream_responses = [(f"data: {json.dumps(response)}\n\n").encode() for response in generate_stream_responses]
        httpx_mock.add_response(
            url=match_endpoint(ServiceInterface.GENERATE),
            stream=IteratorStream(stream_responses),
            headers={"Content-Type": "text/event-stream"},
        )
        expected_text = ""
        for idx, result in enumerate(llm.stream_complete(prompts[0])):
            expected_response = expected_generated_responses[idx]
            expected_delta = expected_response.results[0].generated_text
            expected_text += expected_delta
            assert isinstance(result, CompletionResponse) is True
            assert result.delta == expected_delta
            assert result.text == expected_text
            assert result.additional_kwargs == create_generation_info_from_response(
                expected_response, result=expected_response.results[0]
            )

    def test_llama_index_chat(self, llm, params, messages, httpx_mock: HTTPXMock):
        generate_response = SimpleResponse.generate_chat(
            model_id=self.model,
            messages=messages,
            generated_text="What is a molecule?",
        )
        expected_response = ChatResponse(**generate_response)
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.CHAT), method="POST", json=generate_response)

        result = llm.chat(messages=messages)
        assert isinstance(result, LlamaIndexChatResponse) is True
        assert result.message.content == expected_response.results[0].generated_text
        assert result.additional_kwargs == create_generation_info_from_response(
            expected_response, result=expected_response.results[0]
        )

    def test_llama_index_stream_chat(self, llm, params, messages, httpx_mock: HTTPXMock):
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
        expected_text = ""
        for idx, result in enumerate(llm.stream_chat(messages=messages)):
            expected_response = expected_generated_responses[idx]
            expected_delta = expected_response.results[0].generated_text or ""
            expected_text += expected_delta
            assert isinstance(result, LlamaIndexChatResponse) is True
            assert result.delta == expected_delta
            assert result.message.content == expected_text
            assert result.additional_kwargs == create_generation_info_from_response(
                expected_response, result=expected_response.results[0]
            )

    @pytest.mark.asyncio
    async def test_async_llama_index_interface(self, llm, params, prompts, httpx_mock: HTTPXMock):
        generate_response = SimpleResponse.generate(model=self.model, inputs=prompts, params=params)
        expected_response = GenerateResponse(**generate_response)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=generate_response)

        result = await llm.acomplete(prompts[0])
        assert isinstance(result, CompletionResponse)
        assert result.text == expected_response.results[0].generated_text
