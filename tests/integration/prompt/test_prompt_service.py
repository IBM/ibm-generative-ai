import pytest

from genai import Client
from genai.prompt import ModerationParameters
from genai.text.chat import (
    TextGenerationParameters,
    TextGenerationReturnOptions,
)

TEST_MODEL_ID = "google/flan-t5-xl"
PROMPT_NAME = "My test prompt"


def match_prompt_id(r1, r2):
    assert r1.path == r2.path


@pytest.mark.integration
class TestPromptService:
    @pytest.mark.vcr
    def test_create_delete_prompt(self, client: Client, subtests):
        with subtests.test("Create prompt"):
            template = "Write the recipe for {{meal}} in the style of {{author}}"
            create_response = client.prompt.create(
                model_id=TEST_MODEL_ID,
                name=PROMPT_NAME,
                input=template,
                data={"meal": "goulash", "author": "Shakespeare"},
                moderations=ModerationParameters(),
            )
            prompt_id = create_response.result.id

        with subtests.test("Get prompt"):
            retrieve_response = client.prompt.retrieve(id=prompt_id)
            assert retrieve_response.result == create_response.result

        with subtests.test("Use prompt"):
            [generation_response] = list(
                client.text.generation.create(
                    prompt_id=prompt_id,
                    parameters=TextGenerationParameters(return_options=TextGenerationReturnOptions(input_text=True)),
                )
            )
            [result] = generation_response.results
            assert result.input_text == template.replace("{{meal}}", "goulash").replace("{{author}}", "Shakespeare")

        with subtests.test("Delete prompt"):
            client.prompt.delete(id=prompt_id)

        with subtests.test("Prompt was deleted"):
            for prompt in client.prompt.list(search=PROMPT_NAME, model_id=TEST_MODEL_ID, limit=None).results:
                assert prompt.id != prompt_id
