import logging
from typing import Optional

import pytest

from genai.client import Client
from genai.schema import (
    StopReason,
    TextGenerationParameters,
    TextGenerationResult,
    TextTokenizationCreateResults,
    TextTokenizationParameters,
)

logger = logging.getLogger(__name__)

# Test the implementation of CustomModel class


@pytest.mark.integration
class TestLocalServer:
    def test_local_server(self):
        from genai.extensions.localserver import LocalLLMServer, LocalModel

        class ExampleModel(LocalModel):
            model_id = "example/model"

            def __init__(self):
                logger.info("Initialising my custom model")

            def generate(self, input_text: str, parameters: Optional[TextGenerationParameters]) -> TextGenerationResult:
                logger.info(f"Calling generate on: {input_text}")

                genai_response = TextGenerationResult(
                    generated_text=input_text,
                    generated_token_count=len(input_text.split(" ")),
                    input_token_count=len(input_text.split(" ")),
                    stop_reason=StopReason.EOS_TOKEN,
                )
                logger.info(f"Response to {input_text} was: {genai_response}")

                return genai_response

            def tokenize(
                self, input_text: str, parameters: Optional[TextTokenizationParameters]
            ) -> TextTokenizationCreateResults:
                logger.info(f"Calling tokenize on: {input_text}")
                tokens = input_text.split(" ")
                result = TextTokenizationCreateResults(token_count=len(tokens))
                if parameters and parameters.return_options and parameters.return_options.tokens is True:
                    result.tokens = tokens
                return result

        # Instantiate the Local Server with your model
        server = LocalLLMServer(models=[ExampleModel])
        # Start the server and execute your code
        with server.run_locally():
            logger.info("Local Server Started, attempting basic generate call")
            # Get the credentials / connection details for the local server
            client = Client(credentials=server.get_credentials())

            test_prompt = "hello this is a test of a custom model in a local server"
            responses = list(client.text.generation.create(model_id=ExampleModel.model_id, inputs=[test_prompt]))
            assert len(responses) == 1
            # Our test model simply returns the input test, so this will verify that our server is working
            assert len(responses[0].results) == 1
            assert responses[0].results[0].generated_text == test_prompt

            token_responses = list(client.text.tokenization.create(input=[test_prompt], model_id=ExampleModel.model_id))
            assert len(token_responses) == 1
            assert len(token_responses[0].results) == 1
            assert token_responses[0].results[0].token_count == len(test_prompt.split(" "))
