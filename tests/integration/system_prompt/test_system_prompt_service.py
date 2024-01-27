import pytest

from genai.client import Client


@pytest.mark.integration
class TestSystemPromptService:
    @pytest.mark.vcr
    def test_create_delete_system_prompt(self, client: Client, subtests):
        with subtests.test("Create system prompt"):
            create_response = client.system_prompt.create(
                name="My system prompt", content="My system prompt description"
            )
            id = create_response.result.id

        with subtests.test("Get system prompt"):
            retrieve_response = client.system_prompt.retrieve(id=id)
            assert retrieve_response.result == create_response.result

        with subtests.test("List system prompts"):
            system_prompt_ids = [system_prompt.id for system_prompt in client.system_prompt.list().results]
            assert id in system_prompt_ids

        with subtests.test("Delete system prompt"):
            client.system_prompt.delete(id=id)

        with subtests.test("Verify the system prompt deletion"):
            for system_prompt in client.system_prompt.list().results:
                assert system_prompt.id != id
