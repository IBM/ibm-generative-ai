import json
from unittest.mock import MagicMock

import pytest
from langchain.callbacks.base import BaseCallbackHandler
from pytest_httpx import HTTPXMock, IteratorStream

from genai import Credentials
from genai.schemas import GenerateParams
from genai.schemas.responses import GenerateResponse, GenerateStreamResponse
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint


@pytest.mark.extension
class TestLangChain:
    def setup_method(self):
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def credentials(self):
        return Credentials("GENAI_APY_KEY")

    @pytest.fixture
    def params(self):
        return GenerateParams()

    @pytest.fixture
    def prompts(self):
        return ["Hi! How's the weather, eh?"]

    @pytest.fixture
    def multi_prompts(self):
        return ["What is IBM?", "What is AI?"]

    def test_langchain_interface(self, credentials, params, prompts, httpx_mock: HTTPXMock):
        from genai.extensions.langchain import LangChainInterface

        GENERATE_RESPONSE = SimpleResponse.generate(model="google/flan-ul2", inputs=prompts, params=params)
        expected_response = GenerateResponse(**GENERATE_RESPONSE)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=GENERATE_RESPONSE)

        model = LangChainInterface(model="google/flan-ul2", params=params, credentials=credentials)
        results = model(prompts[0])
        assert results == expected_response.results[0].generated_text

    @pytest.mark.asyncio
    async def test_async_langchain_interface(self, credentials, params, multi_prompts, httpx_mock: HTTPXMock):
        from genai.extensions.langchain import LangChainInterface

        GENERATE_RESPONSE = SimpleResponse.generate(model="google/flan-ul2", inputs=multi_prompts, params=params)
        expected_response = GenerateResponse(**GENERATE_RESPONSE)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=GENERATE_RESPONSE)

        model = LangChainInterface(model="google/flan-ul2", params=params, credentials=credentials)
        observed = await model.agenerate(prompts=multi_prompts)
        assert len(observed.generations) == 2
        assert len(observed.generations[0]) == 1
        assert len(observed.generations[1]) == 1

        assert observed.llm_output["token_usage"]["input_token_count"] == sum(
            c.input_token_count for c in expected_response.results
        )
        assert observed.llm_output["token_usage"]["generated_token_count"] == sum(
            c.generated_token_count for c in expected_response.results
        )

        for idx, generation_list in enumerate(observed.generations):
            assert len(generation_list) == 1
            generation = generation_list[0]
            assert generation.text == expected_response.results[idx].generated_text

            expected_result = expected_response.results[idx].model_dump()
            for key in {"generated_token_count", "input_text", "stop_reason"}:
                assert generation.generation_info[key] == expected_result[key]

    def test_langchain_stream(self, credentials, params, prompts, httpx_mock: HTTPXMock):
        from genai.extensions.langchain import LangChainInterface

        GENERATE_STREAM_RESPONSES = SimpleResponse.generate_stream(
            model="google/flan-ul2", inputs=prompts, params=params
        )
        expected_generated_responses = [GenerateStreamResponse(**result) for result in GENERATE_STREAM_RESPONSES]
        stream_responses = [(f"data: {json.dumps(response)}\n\n").encode() for response in GENERATE_STREAM_RESPONSES]
        httpx_mock.add_response(
            url=match_endpoint(ServiceInterface.GENERATE),
            stream=IteratorStream(stream_responses),
            headers={"Content-Type": "text/event-stream"},
        )

        callback = BaseCallbackHandler()
        callback.on_llm_new_token = MagicMock()

        model = LangChainInterface(
            model="google/flan-ul2",
            params=params,
            credentials=credentials,
            callbacks=[callback],
        )

        # Verify results
        for idx, result in enumerate(model.stream(input=prompts[0])):
            expected_result = expected_generated_responses[idx]
            assert result == expected_result.results[0].generated_text

        # Verify that callbacks were called
        assert callback.on_llm_new_token.call_count == len(expected_generated_responses)
        for idx, result in enumerate(expected_generated_responses):
            retrieved_kwargs = callback.on_llm_new_token.call_args_list[idx].kwargs
            token = retrieved_kwargs["token"]
            assert token == result.results[0].generated_text
            response = retrieved_kwargs["response"]
            assert response == result.results[0]

    def test_prompt_translator(self):
        from langchain.prompts import PromptTemplate

        import genai.extensions.langchain  # noqa
        from genai.prompt_pattern import PromptPattern

        s = "My name is {name}. I work for {company}. I live in {city}."
        pt = PromptTemplate(input_variables=["name", "company", "city"], template=s)
        pattern = PromptPattern.langchain.from_template(pt)
        assert pattern.find_vars() == {"name", "company", "city"}
        ptemp = pattern.langchain.as_template()
        assert set(ptemp.input_variables) == {"name", "company", "city"}
        assert ptemp.template == s
