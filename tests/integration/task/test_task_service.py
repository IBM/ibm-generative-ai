import pytest

from genai import Client


@pytest.mark.integration
class TestTaskService:
    @pytest.mark.vcr
    def test_list_tasks(self, client: Client) -> None:
        response = client.task.list()
        assert response
