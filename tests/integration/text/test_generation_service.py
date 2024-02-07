import pytest

from genai import Client
from genai.schema import (
    DecodingMethod,
    LengthPenalty,
    ModerationHAP,
    ModerationImplicitHate,
    ModerationParameters,
    ModerationStigma,
    TextGenerationComparisonCreateRequestRequest,
    TextGenerationComparisonParameters,
    TextGenerationParameters,
    TextGenerationReturnOptions,
)

TEST_MODEL_ID = "google/flan-t5-xxl"


@pytest.mark.integration
class TestGenerationService:
    @pytest.mark.vcr
    def test_create(self, client: Client):
        """Text generation works correctly."""
        prompt = "Here is a funny short joke about AI: "
        generator = client.text.generation.create(
            model_id=TEST_MODEL_ID,
            inputs=[prompt],
            parameters=TextGenerationParameters(
                decoding_method=DecodingMethod.SAMPLE,
                max_new_tokens=40,
                min_new_tokens=1,
                top_k=50,
                top_p=1,
                return_options=TextGenerationReturnOptions(input_text=True, input_tokens=False),
                temperature=0.5,
            ),
        )
        [result] = list(generator)
        assert result.results[0].input_text == prompt

    @pytest.mark.vcr
    def test_create_stream(self, client: Client):
        """Streaming works correctly."""
        prompt = "Poop stinks. This is why my favorite color is green: "
        min_tokens, max_tokens = 3, 10
        generator = client.text.generation.create_stream(
            model_id=TEST_MODEL_ID,
            input=prompt,
            moderations=ModerationParameters(hap=ModerationHAP(input=True, output=True, send_tokens=True)),
            parameters=TextGenerationParameters(
                decoding_method=DecodingMethod.SAMPLE,
                max_new_tokens=max_tokens,
                min_new_tokens=min_tokens,
                return_options=TextGenerationReturnOptions(input_text=True, input_tokens=False),
                temperature=0,
            ),
        )
        all_responses = list(generator)
        # First token is empty
        [first_empty] = all_responses.pop(0).results
        assert first_empty.generated_text == ""

        # Some results contain only response
        responses_with_result = [response for response in all_responses if response.results]
        assert all(len(response.results) == 1 for response in responses_with_result)
        assert all(response.moderation is None for response in responses_with_result)
        assert min_tokens <= len(responses_with_result) <= max_tokens

        # Other results contain only moderations
        responses_without_result = [response for response in all_responses if response.results is None]
        assert all(len(response.moderation.hap) == 1 for response in responses_without_result)
        assert all(response.results is None for response in responses_without_result)
        assert len(responses_without_result) >= 0
        assert any(result.moderation.hap[0].flagged for result in responses_without_result)

    @pytest.mark.vcr
    def test_compare(self, client: Client):
        length_penalty_1 = LengthPenalty(decay_factor=1.2, start_index=50).model_dump()
        length_penalty_2 = LengthPenalty(decay_factor=1.5, start_index=50).model_dump()

        comparison = client.text.generation.compare(
            request=TextGenerationComparisonCreateRequestRequest(
                moderations=ModerationParameters(
                    hap=ModerationHAP(input=True, output=True, send_tokens=True),
                    implicit_hate=ModerationImplicitHate(input=True, output=True, send_tokens=True, threshold=0.7),
                    stigma=ModerationStigma(input=True, output=True),
                ),
                model_id=TEST_MODEL_ID,
                input="hahaha",
            ),
            compare_parameters=TextGenerationComparisonParameters(
                length_penalty=[length_penalty_1, length_penalty_2],
                temperature=[0.5, 1],
            ),
            name="my comparison",
        )
        assert len(comparison.results) == 4
        any(res.parameters.length_penalty == length_penalty_1 for res in comparison.results)
        any(res.parameters.length_penalty == length_penalty_2 for res in comparison.results)
        any(res.parameters.temperature == 0.5 for res in comparison.results)
        any(res.parameters.temperature == 1 for res in comparison.results)
