import logging
from typing import Optional, Union

import pytest

from genai import Options, PromptPattern
from genai.client import Client, ServicesContainer
from genai.extensions.localserver.local_client import LocalClient
from genai.schemas import GenerateParams, GenerateResult, TokenizeResult, TokenParams
from genai.services.generate_service import GenerationService, Params
from genai.services.tokenize_service import TokenizeService

logger = logging.getLogger(__name__)


# Test implementation of CustomModel class


@pytest.mark.extension
class TestLocalServer:
    def test_local_server(self):
        from genai.extensions.localserver import LocalLLMServer

        class ExampleGenerationService(GenerationService):
            def generate(
                self,
                model: str,
                prompts: Union[list[str], list[PromptPattern]],
                params: Params,
                options: Optional[Options] = None,
            ) -> list[GenerateResult]:
                input_text = prompts[0]
                logger.info(f"Calling generate on: {input_text}")

                genai_response = GenerateResult(
                    generated_text=input_text,
                    generated_token_count=len(input_text.split(" ")),
                    input_token_count=len(input_text.split(" ")),
                    stop_reason="",
                )
                logger.info(f"Response to {input_text} was: {genai_response}")

                return [genai_response]

        class ExampleTokenizeService(TokenizeService):
            def tokenize(
                self,
                model_id: str,
                prompts: Union[list[str], list[PromptPattern]],
                params: Optional[TokenParams] = None,
                options: Optional[Options] = None,
            ) -> list[TokenizeResult]:
                results = []
                for input_text in prompts:
                    logger.info(f"Calling tokenize on: {input_text}")
                    tokens = input_text.split(" ")
                    result = TokenizeResult(token_count=len(tokens))
                    if params and params.return_tokens is True:
                        result.tokens = tokens
                    results.append(result)
                return results

        # Instantiate the Local Server with custom client/services
        client = LocalClient(
            services=ServicesContainer(generation=ExampleGenerationService, tokenize=ExampleTokenizeService),
        )
        server = LocalLLMServer(client=client)

        # Start the server and execute your code
        with server.run_locally():
            logger.info("Local Server Started, attempting basic generate call")
            # Get the credentials / connection details for the local server
            creds = server.get_credentials()

            # Instantiate parameters for text generation
            params = GenerateParams()

            # Instantiate a model proxy object to send your requests
            client = Client(credentials=creds)

            test_prompt = "hello this is a test of a custom model in a local server"
            responses = client.generation.generate(model="example/model", prompts=[test_prompt], params=params)
            assert len(responses) == 1
            # Our test model simply returns the input test, so this will verify that our server is working
            assert responses[0].generated_text == test_prompt

            token_responses = client.tokenize.tokenize(model_id="example/model", prompts=[test_prompt])
            assert len(token_responses) == 1
            token_response = token_responses[0]
            # Our test model simply returns the input test, so this will verify that our server is working
            assert token_response.token_count == len(test_prompt.split(" "))
