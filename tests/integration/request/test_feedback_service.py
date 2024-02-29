import pytest

from genai import Client
from genai.schema import RequestFeedbackVote, TextGenerationFeedbackCategory

TEST_MODEL_ID = "google/flan-t5-xl"


@pytest.mark.integration
class TestFeedbackService:
    @pytest.mark.vcr
    def test_create_update_retrieve(self, client: Client, subtests) -> None:
        """Text generation works correctly."""

        gen_res = client.text.generation.create(model_id=TEST_MODEL_ID, inputs=["2+3="], parameters={"temperature": 0})
        generation_id = list(gen_res)[0].id
        assert generation_id is not None

        with subtests.test("Create feedback"):
            comment = "Well done."
            vote = RequestFeedbackVote.UP
            result_create = client.request.feedback.create(
                generation_id, categories=[TextGenerationFeedbackCategory.CORRECT_CONTENT], comment=comment, vote=vote
            ).result
            assert result_create.categories == [TextGenerationFeedbackCategory.CORRECT_CONTENT]
            assert result_create.comment == comment
            assert result_create.vote == vote

        with subtests.test("Update feedback"):
            comment = "I'm not sure about the category"
            vote = RequestFeedbackVote.DOWN
            result_update = client.request.feedback.update(
                generation_id, categories=[TextGenerationFeedbackCategory.CORRECT_STYLE], comment=comment, vote=vote
            ).result
            assert result_update.categories == [TextGenerationFeedbackCategory.CORRECT_STYLE]
            assert result_update.comment == comment
            assert result_update.vote == vote

        with subtests.test("Retrieve feedback"):
            result_retrieve = client.request.feedback.retrieve(generation_id).result
            assert result_retrieve.categories == [TextGenerationFeedbackCategory.CORRECT_STYLE]
            assert result_retrieve.comment == comment
