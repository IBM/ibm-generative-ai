import pytest

from genai import Client


@pytest.mark.integration
class TestTagService:
    @pytest.mark.vcr
    def test_list_tags(self, client: Client) -> None:
        first_page = client.tag.list(limit=5, offset=0)
        rest_tags = client.tag.list(limit=None, offset=5)

        all_tags = client.tag.list(limit=None)
        assert len(first_page.results) == 5
        assert all_tags.results == first_page.results + rest_tags.results
        assert all_tags.results[0].id