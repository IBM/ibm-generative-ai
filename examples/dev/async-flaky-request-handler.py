import asyncio
import logging
import os
import random

import httpx
from dotenv import load_dotenv

from genai.model import Credentials, Model
from genai.schemas import GenerateParams, TokenParams
from genai.services.connection_manager import ConnectionManager
from genai.services.request_handler import RequestHandler

logging.basicConfig(level="ERROR")


class FlakyRequestHandler(RequestHandler):
    @staticmethod
    async def flaky_async_generate(
        endpoint: str, key: str, model_id: str = None, inputs: list = None, parameters: dict = None, options=None
    ):
        """Low level API for async /generate request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            model_id (str, optional): The id of the language model to be queried. Defaults to None.
            inputs (list, optional): List of inputs to be queried. Defaults to None.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.
            options (Options, optional): Additional parameters to pass in the query payload. Defaults to None.

        Returns:
            httpx.Response: Response from the REST API.
        """
        headers, json_data, _ = RequestHandler._metadata(
            method="POST",
            key=key,
            model_id=model_id,
            inputs=inputs,
            parameters=parameters,
            options=options,
        )

        response = None
        totalsleep = 0
        for attempt in range(0, ConnectionManager.MAX_RETRIES_GENERATE):
            response = await ConnectionManager.async_generate_client.post(endpoint, headers=headers, json=json_data)
            choice = random.randint(0, 2)
            if choice == 0:
                response.status_code = httpx.codes.SERVICE_UNAVAILABLE
            elif choice == 1:
                response.status_code = httpx.codes.TOO_MANY_REQUESTS
            else:
                pass
            if response.status_code in [httpx.codes.SERVICE_UNAVAILABLE, httpx.codes.TOO_MANY_REQUESTS]:
                totalsleep += 2 ** (attempt + 1)
                print(
                    "Prompt = {}, Choice = {}, Current sleep {} seconds, Total sleep = {}".format(
                        json_data["inputs"], choice, 2 ** (attempt + 1), totalsleep
                    )
                )
                await asyncio.sleep(2 ** (attempt + 1))
            else:
                break
        return response


RequestHandler.async_generate = FlakyRequestHandler.flaky_async_generate

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key=api_key, api_endpoint=api_url)  # credentials object to access GENAI


# Instantiate parameters for text generation
generate_params = GenerateParams(decoding_method="sample", max_new_tokens=5, min_new_tokens=1)
tokenize_params = TokenParams(return_tokens=True)


flan_ul2 = Model("google/flan-ul2", params=generate_params, credentials=creds)
prompts = ["Generate a random number > {}: ".format(i) for i in range(25)]
for response in flan_ul2.generate_async(prompts, ordered=True):
    pass
