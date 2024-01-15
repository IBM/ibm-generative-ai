from typing import Optional

import pytest

from genai import Client
from genai.text.tokenization import (
    TextTokenizationParameters,
    TextTokenizationReturnOptions,
)

TEST_MODEL_ID = "google/flan-t5-xl"


@pytest.mark.integration
class TestTokenizationService:
    TEST_INPUTS = [
        "What did the large language model say to its programmer?",
        "I'm sorry, I'm feeling a bit recursive today. Can you give me a break... statement?",
    ]

    @staticmethod
    def _get_text_from_tokens(tokens: Optional[list[str]] = None) -> str:
        if not tokens:
            return ""
        return "".join(t.replace("▁", " ") for t in tokens).replace("</s>", "").strip()

    @pytest.mark.vcr
    def test_create_tokenization_single_input(self, client: Client) -> None:
        test_input = " ".join(self.TEST_INPUTS)
        [response] = list(
            client.text.tokenization.create(
                input=test_input,
                parameters=TextTokenizationParameters(return_options=TextTokenizationReturnOptions(tokens=True)),
                model_id=TEST_MODEL_ID,
            )
        )
        assert response.model_id == TEST_MODEL_ID
        assert response.results
        [result] = response.results
        assert self._get_text_from_tokens(result.tokens) == test_input
        assert result.token_count == len(result.tokens or [])

    @pytest.mark.vcr
    def test_create_tokenization_multiple_inputs(self, client: Client) -> None:
        [response] = list(
            client.text.tokenization.create(
                input=self.TEST_INPUTS,
                parameters=TextTokenizationParameters(return_options=TextTokenizationReturnOptions(tokens=True)),
                model_id=TEST_MODEL_ID,
            )
        )
        assert response.model_id == TEST_MODEL_ID
        assert response.results

        assert len(response.results) == len(self.TEST_INPUTS)
        for result, test_input in zip(response.results, self.TEST_INPUTS):
            assert self._get_text_from_tokens(result.tokens) == test_input
            assert result.token_count == len(result.tokens or [])
