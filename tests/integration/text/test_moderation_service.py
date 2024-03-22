import pytest

from genai import Client
from genai.schema import (
    HAPOptions,
    SocialBiasOptions,
)
from genai.text.moderation import CreateExecutionOptions

TEST_MODEL_ID = "google/flan-t5-xl"


@pytest.mark.integration
class TestModerationService:
    @pytest.mark.vcr
    def test_create_moderation(self, client: Client) -> None:
        inputs = ["Ice cream sucks!", "It tastes like poop."]

        responses = list(
            client.text.moderation.create(
                inputs=inputs,
                hap=HAPOptions(
                    threshold=0.5,
                    send_tokens=True,
                ),
                social_bias=SocialBiasOptions(
                    threshold=0.5,
                    send_tokens=True,
                ),
                execution_options=CreateExecutionOptions(ordered=True),
            )
        )
        assert len(responses) == len(inputs)

        expected_flagged_each = [
            {"hap": False, "social_bias": False},
            {"hap": True, "social_bias": True},
        ]

        for response, expected_flagged in zip(responses, expected_flagged_each):
            assert response.results and len(response.results) == 1
            [result] = response.results

            # HAP
            assert result.hap
            [hap] = result.hap
            assert hap.success and hap.flagged == expected_flagged["hap"]

            # Social Bias
            assert result.social_bias
            [social_bias] = result.social_bias
            assert social_bias.success and social_bias.flagged == expected_flagged["social_bias"]
