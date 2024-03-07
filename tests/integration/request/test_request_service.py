import pytest

from genai import Client
from genai.schema import HumanMessage, RequestStatus

TEST_MODEL_ID = "google/flan-t5-xl"


@pytest.mark.integration
class TestRequestService:
    @pytest.mark.vcr
    def test_create_retrieve_delete_record(self, client: Client, subtests):
        # Create a text generation request
        generate_input = "Hello Marvin, how are you today?"
        [generation_response] = list(
            client.text.generation.create(
                model_id=TEST_MODEL_ID,
                inputs=generate_input,
                parameters={"max_new_tokens": 10},
            )
        )

        with subtests.test("Retrieve generate call from list endpoint"):
            response = client.request.list(limit=1, offset=0, status=RequestStatus.SUCCESS)
            [result] = response.results
            assert result.id == generation_response.id
            assert result.status == RequestStatus.SUCCESS
            assert result.request == {
                "input": generate_input,
                "model_id": TEST_MODEL_ID,
                "parameters": {"max_new_tokens": 10},
            }

        with subtests.test("Delete generate record"):
            client.request.delete(id=generation_response.id)

        with subtests.test("Deleted record is no longer available"):
            response = client.request.list(limit=1, offset=0, status=RequestStatus.SUCCESS)
            for result in response.results:
                assert result.id != generation_response.id

    @pytest.mark.vcr
    def test_create_retrieve_delete_chat_record(self, client: Client, subtests):
        # Create a text generation request
        message = HumanMessage(content="Hello Marvin, how are you today?")
        chat = client.text.chat.create(
            model_id=TEST_MODEL_ID,
            messages=[message],
            parameters={"max_new_tokens": 10},
        )

        with subtests.test("Retrieve chat record"):
            response = client.request.chat(chat.conversation_id)
            [result] = response.results
            assert result.id == chat.id
            assert result.status == RequestStatus.SUCCESS
            [result_message] = result.request.messages
            assert result_message["content"] == message.content

        with subtests.test("Delete chat"):
            client.request.chat_delete(conversation_id=chat.conversation_id)

        with subtests.test("Record was actually deleted"):
            response = client.request.chat(conversation_id=chat.conversation_id)
            assert response.results == []
