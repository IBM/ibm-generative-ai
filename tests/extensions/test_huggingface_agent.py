import pytest
from pytest_httpx import HTTPXMock

from genai import Credentials
from genai.extensions.huggingface import IBMGenAIAgent
from genai.schemas import GenerateParams
from genai.services import ServiceInterface
from genai.utils.request_utils import match_endpoint
from tests.assets.response_helper import SimpleResponse


@pytest.mark.extension
class TestHuggingfaceAgent:
    @pytest.fixture
    def credentials(self):
        return Credentials("GENAI_APY_KEY")

    @pytest.fixture
    def params(self):
        return GenerateParams()

    @pytest.fixture
    def mock_model_response(self):
        return [
            """tool: `summarizer` to create a summary of the input text.
        Answer:
        ```py
        summarized_text = summarizer(text)
        print(f"Summary: {summarized_text}")
        ```

        Task:"""
        ]

    def test_agent(self, credentials, params, mock_model_response, httpx_mock: HTTPXMock):
        GENERATE_RESPONSE = SimpleResponse.generate(
            model="google/flan-ul2",
            inputs=mock_model_response,
            params=params,
        )
        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=GENERATE_RESPONSE)
        agent = IBMGenAIAgent(credentials=credentials, model="google/flan-ul2", params=params)
        agent.run("Summarize the text", text="Testing the summarization")
