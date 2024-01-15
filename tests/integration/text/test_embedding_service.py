import pytest

from genai import Client
from genai.text.embedding import CreateExecutionOptions

TEST_MODEL_ID = "sentence-transformers/all-minilm-l6-v2"


@pytest.mark.integration
class TestEmbeddingService:
    @pytest.mark.vcr
    def test_create_embedding(self, client: Client) -> None:
        """Embedding works correctly."""
        inputs = ["Hello", "world"]

        responses = list(
            client.text.embedding.create(
                inputs=inputs,
                model_id=TEST_MODEL_ID,
                execution_options=CreateExecutionOptions(ordered=True),
            )
        )

        assert len(responses) == len(inputs)
