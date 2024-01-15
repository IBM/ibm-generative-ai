import pytest

from genai import Client
from genai.text.moderation import (
    CreateExecutionOptions,
    HAPOptions,
    ImplicitHateOptions,
    StigmaOptions,
)

TEST_MODEL_ID = "google/flan-t5-xl"


@pytest.mark.integration
class TestModerationService:
    @pytest.mark.vcr
    def test_create_moderation(self, client: Client) -> None:
        inputs = ["Ice cream sucks!", "It tastes like poop."]

        responses = list(
            client.text.moderation.create(
                inputs=inputs,
                hap=HAPOptions(threshold=0.5, send_tokens=True),
                implicit_hate=ImplicitHateOptions(threshold=0.5, send_tokens=True),
                stigma=StigmaOptions(threshold=0.5, send_tokens=True),
                execution_options=CreateExecutionOptions(ordered=True),
            )
        )
        assert len(responses) == len(inputs)

        expected_flagged_each = [
            {"hap": False, "stigma": False, "implicit_hate": False},
            {"hap": True, "stigma": True, "implicit_hate": True},
        ]

        for response, expected_flagged in zip(responses, expected_flagged_each):
            assert response.results and len(response.results) == 1
            [result] = response.results

            # HAP
            assert result.hap
            [hap] = result.hap
            assert hap.success and hap.flagged == expected_flagged["hap"]

            # Stigma
            assert result.stigma
            [stigma] = result.stigma
            assert stigma.success and stigma.flagged == expected_flagged["stigma"]

            # Implicit Hate
            assert result.implicit_hate
            [implicit_hate] = result.implicit_hate
            assert implicit_hate.success and implicit_hate.flagged == expected_flagged["implicit_hate"]
