from unittest.mock import MagicMock

import pytest
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import GenerationChunk

from genai import Client
from genai._generated.api import TextGenerationCreateResponse
from genai._generated.endpoints import (
    TextGenerationCreateEndpoint,
    TextGenerationStreamCreateEndpoint,
)
from genai.extensions.langchain import LangChainInterface
from genai.text.generation import (
    TextGenerationParameters,
    TextGenerationStreamCreateResponse,
)


@pytest.mark.integration
class TestLangChain:
    def setup_method(self):
        self.model_id = "google/flan-ul2"

    @pytest.fixture
    def parameters(self):
        return TextGenerationParameters()

    @pytest.fixture
    def langchain_model(self, client: Client, parameters: TextGenerationParameters):
        return LangChainInterface(model_id=self.model_id, parameters=parameters, client=client)

    @pytest.mark.vcr
    def test_langchain_interface(self, langchain_model, get_vcr_responses_of):
        result = langchain_model("Monday, Tuesday, Wednesday, ")
        [expected_response] = get_vcr_responses_of(TextGenerationCreateEndpoint)
        assert result == expected_response["results"][0]["generated_text"]

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_async_langchain_interface(self, langchain_model, get_vcr_responses_of):
        prompts = [
            "one, two, three, ",
            "a, b, c, d, ",
        ]
        observed = await langchain_model.agenerate(prompts=prompts)
        assert len(observed.generations) == 2
        assert len(observed.generations[0]) == 1
        assert len(observed.generations[1]) == 1

        raw_responses = get_vcr_responses_of(TextGenerationCreateEndpoint)
        api_responses = [TextGenerationCreateResponse.model_validate(response) for response in raw_responses]
        assert all(len(response.results) == 1 for response in api_responses)

        generated_token_count = sum(response.results[0].generated_token_count for response in api_responses)
        input_token_count = sum(response.results[0].input_token_count for response in api_responses)

        assert observed.llm_output["token_usage"] == {
            "prompt_tokens": input_token_count,
            "completion_tokens": generated_token_count,
            "total_tokens": generated_token_count + input_token_count,
        }

        for idx, generation_list in enumerate(observed.generations):
            assert len(generation_list) == 1
            generation = generation_list[0]
            [expected_result] = api_responses[idx].results
            assert generation.text == expected_result.generated_text

            for key in {"stop_reason"}:
                assert generation.generation_info[key] == getattr(expected_result, key)

    @pytest.mark.vcr
    def test_langchain_stream(self, parameters, client: Client, get_vcr_responses_of):
        prompts = ["Monday, Tuesday, Wednesday, "]
        callback = BaseCallbackHandler()
        callback.on_llm_new_token = MagicMock()

        model = LangChainInterface(model_id=self.model_id, parameters=parameters, client=client, callbacks=[callback])
        model_results = list(model.stream(input=prompts[0]))

        raw_responses = get_vcr_responses_of(TextGenerationStreamCreateEndpoint)
        api_responses = [TextGenerationStreamCreateResponse.model_validate(response) for response in raw_responses]
        # Verify results
        for idx, api_response in enumerate(model_results):
            expected_result = api_responses[idx]
            assert api_response == expected_result.results[0].generated_text

        # Verify that callbacks were called
        assert callback.on_llm_new_token.call_count == len(api_responses)
        for idx, api_response in enumerate(api_responses):
            retrieved_kwargs = callback.on_llm_new_token.call_args_list[idx].kwargs
            token = retrieved_kwargs["token"]
            assert token == api_response.results[0].generated_text
            chunk = retrieved_kwargs["chunk"]
            assert isinstance(chunk, GenerationChunk)
            response = retrieved_kwargs["response"]
            assert response == api_response
