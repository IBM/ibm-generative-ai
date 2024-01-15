import pytest

from genai import Client
from genai.text.chat import (
    HumanMessage,
    ModerationHAP,
    ModerationParameters,
    TextGenerationParameters,
)

TEST_MODEL_ID = "meta-llama/llama-2-13b-chat"


@pytest.mark.integration
class TestChatService:
    @pytest.mark.vcr
    def test_create_history(self, client: Client, subtests):
        with subtests.test("Start a conversation"):
            human_message = HumanMessage(content="Do you want to destroy the world?")
            chat = client.text.chat.create(messages=[human_message], model_id=TEST_MODEL_ID)
            [chat_result] = chat.results
            ai_message = chat_result.generated_text
            assert ai_message
            assert "no" in ai_message.lower()  # AI is still safe for humanity

        with subtests.test("Get history of the conversation"):
            history = client.request.chat(chat.conversation_id)
            [history_result] = history.results
            assert history_result.request.messages and history_result.response.results
            [request_message] = history_result.request.messages
            [response_message] = history_result.response.results
            assert request_message.model_dump(exclude="tokens") == human_message.model_dump()
            assert response_message.generated_text == ai_message

        with subtests.test("Continue previous conversation"):
            human_message_2 = HumanMessage(content="What was my previous question?")
            new_chat = client.text.chat.create(
                conversation_id=chat.conversation_id, messages=[human_message_2], model_id=TEST_MODEL_ID
            )
            assert new_chat.conversation_id == chat.conversation_id
            [chat_result] = new_chat.results
            ai_message_2 = chat_result.generated_text
            assert ai_message_2
            assert human_message.content.lower() in ai_message_2.lower()

        with subtests.test("History contains new entries"):
            prev_history_result = history_result
            history = client.request.chat(chat.conversation_id)
            history_result_1, history_result_2 = history.results
            assert history_result_1 == prev_history_result
            assert history_result_2.request.messages and history_result_2.response.results
            [request_message] = history_result_2.request.messages
            [response_message] = history_result_2.response.results
            assert request_message.model_dump(exclude="tokens") == human_message_2.model_dump()
            assert response_message.generated_text == ai_message_2

    @pytest.mark.vcr
    def test_create_stream(self, client):
        min_tokens, max_tokens = 3, 10
        human_message = HumanMessage(content="Poop stinks, doesn't it?")

        generator = client.text.chat.create_stream(
            messages=[human_message],
            model_id=TEST_MODEL_ID,
            parameters=TextGenerationParameters(min_new_tokens=min_tokens, max_new_tokens=max_tokens),
            moderations=ModerationParameters(hap=ModerationHAP(input=True, output=True, send_tokens=True)),
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
