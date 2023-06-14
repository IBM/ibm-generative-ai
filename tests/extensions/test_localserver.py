import logging

import pytest

from genai.model import Model
from genai.schemas import GenerateParams, GenerateResult, TokenizeResult, TokenParams

logger = logging.getLogger(__name__)


# Test implmentation of CustomModel class


@pytest.mark.extension
class TestLocalServer:
    def test_local_server(self):
        from genai.extensions.localserver import CustomModel, LocalLLMServer

        class ExampleModel(CustomModel):
            model_id = "example/model"

            def __init__(self):
                logger.info("Initialising my custom model")

            def generate(self, input_text: str, params: GenerateParams) -> GenerateResult:
                logger.info(f"Calling generate on: {input_text}")

                genai_response = GenerateResult(
                    generated_text=input_text,
                    generated_token_count=len(input_text.split(" ")),
                    input_token_count=len(input_text.split(" ")),
                    stop_reason="",
                )
                logger.info(f"Response to {input_text} was: {genai_response}")

                return genai_response

            def tokenize(self, input_text: str, params: TokenParams) -> TokenizeResult:
                logger.info(f"Calling tokenize on: {input_text}")
                tokens = input_text.split(" ")
                result = TokenizeResult(token_count=len(tokens))
                if params.return_tokens is True:
                    result.tokens = tokens
                return result

        # Instansiate the Local Server with your model
        server = LocalLLMServer(models=[ExampleModel])
        # Start the server and execute your code
        with server.run_locally():
            logger.info("Local Server Started, attempting basic generate call")
            # Get the credentials / connection details for the local server
            creds = server.get_credentials()

            # Instantiate parameters for text generation
            params = GenerateParams()

            # Instantiate a model proxy object to send your requests
            custom_model = Model(ExampleModel.model_id, params=params, credentials=creds)

            test_prompt = "hello this is a test of a custom model in a local server"
            responses = custom_model.generate([test_prompt])
            assert len(responses) == 1
            response = responses[0]
            # Our test model simply returns the input test, so this will verify that our server is working
            assert response.generated_text == test_prompt

            token_responses = custom_model.tokenize([test_prompt])
            assert len(token_responses) == 1
            token_response = token_responses[0]
            # Our test model simply returns the input test, so this will verify that our server is working
            assert token_response.token_count == len(test_prompt.split(" "))
