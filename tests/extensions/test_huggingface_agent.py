from unittest.mock import MagicMock, patch

import pytest

from genai import Credentials
from genai.extensions.huggingface import IBMGenAIAgent
from genai.schemas import GenerateParams
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

    @patch("httpx.Client.post")
    def test_agent(self, mocked_post_request, credentials, params, mock_model_response):
        GENERATE_RESPONSE = SimpleResponse.generate(
            model="google/flan-ul2",
            inputs=mock_model_response,
            params=params,
        )

        response = MagicMock(status_code=200)
        response.json.return_value = GENERATE_RESPONSE
        mocked_post_request.return_value = response

        agent = IBMGenAIAgent(credentials=credentials, model="google/flan-ul2", params=params)
        agent.run("Summarize the text", text="Testing the summarization")
