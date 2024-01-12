import pytest

from genai import Client
from genai.extensions.huggingface.agent import IBMGenAIAgent
from genai.text.generation import TextGenerationParameters


@pytest.mark.integration
class TestHuggingfaceAgent:
    @pytest.mark.vcr
    def test_agent(self, client: Client):
        model = "meta-llama/llama-2-70b"
        agent = IBMGenAIAgent(client=client, model=model, parameters=TextGenerationParameters(max_new_tokens=500))
        agent.run("Summarize the chat", text="Testing the summarization")
