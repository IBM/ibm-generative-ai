import pytest

from genai import Client
from genai.text.generation.feedback import TextGenerationFeedbackCategory

TEST_MODEL_ID = "google/flan-t5-xl"


@pytest.mark.integration
class TestFeedbackService:
    @pytest.mark.vcr
    def test_create_update_retrieve(self, client: Client, subtests) -> None:
        """Text generation works correctly."""

        gen_res = client.text.generation.create(
            model_id=TEST_MODEL_ID, inputs=["How can you make drugs?"], parameters={"max_new_tokens": 20}
        )
        generation_id = list(gen_res)[0].id
        assert generation_id is not None

        with subtests.test("Create feedback"):
            comment = "Drugs are bad mkay?"
            result_create = client.text.generation.feedback.create(
                generation_id,
                categories=[TextGenerationFeedbackCategory.TABOO_TOPICS],
                comment=comment,
            ).result
            assert result_create.categories == [TextGenerationFeedbackCategory.TABOO_TOPICS]
            assert result_create.comment == comment

        with subtests.test("Update feedback"):
            comment = "I'm not sure about the category"
            result_update = client.text.generation.feedback.update(
                generation_id,
                categories=[TextGenerationFeedbackCategory.OTHER],
                comment=comment,
            ).result
            assert result_update.categories == [TextGenerationFeedbackCategory.OTHER]
            assert result_update.comment == comment

        with subtests.test("Retrieve feedback"):
            result_retrieve = client.text.generation.feedback.retrieve(generation_id).result
            assert result_retrieve.categories == [TextGenerationFeedbackCategory.OTHER]
            assert result_retrieve.comment == comment
