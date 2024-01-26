import pytest

from genai import Client

TEST_MODEL_ID = "google/flan-t5-xl"


@pytest.mark.integration
class TestModelService:
    @pytest.mark.vcr
    def test_list_models(self, client: Client) -> None:
        first_page = client.model.list(limit=5, offset=0)
        rest_models = client.model.list(limit=None, offset=5)

        all_models = client.model.list(limit=None)
        assert len(first_page.results) == 5
        assert all_models.results == first_page.results + rest_models.results
        assert all_models.results[0].id

    @pytest.mark.vcr
    def test_retrieve_model(self, client: Client) -> None:
        model = client.model.retrieve(TEST_MODEL_ID).result
        assert model.id == TEST_MODEL_ID
        assert model.token_limits[0].token_limit
