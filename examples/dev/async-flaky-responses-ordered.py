import asyncio
import logging
import os
import random

from dotenv import load_dotenv

from genai.model import Credentials, GenAiException, Model
from genai.schemas import GenerateParams, ModelType, TokenParams
from genai.services.async_generator import AsyncResponseGenerator

num_requests = 0


class FlakyAsyncResponseGenerator(AsyncResponseGenerator):
    async def _get_response_json(self, model, inputs, params):
        try:
            global num_requests
            num_requests += 1
            if num_requests % 2 == 0:
                await asyncio.sleep(random.randint(0, 5))
                response_raw = await self.service_fn_(model, inputs, params)
            else:
                await asyncio.sleep(random.randint(0, 5))
                response_raw = None  # bad response
            response = response_raw.json()
        except Exception as _:  # noqa
            response = None
        return response


class FlakyModel(Model):
    def generate_async(
        self,
        prompts,
        ordered: bool = False,
        callback=None,
    ):
        try:
            with FlakyAsyncResponseGenerator(
                self.model, prompts, self.params, self.service, ordered=ordered, callback=callback
            ) as asynchelper:
                for response in asynchelper.generate_response():
                    yield response
        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)

    def tokenize_async(self, prompts, ordered=False, callback=None):
        try:
            with FlakyAsyncResponseGenerator(
                self.model, prompts, self.params, self.service, fn="tokenize", ordered=ordered, callback=callback
            ) as asynchelper:
                for response in asynchelper.generate_response():
                    yield response
        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)


logging.getLogger("genai").setLevel(logging.INFO)


# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
creds = Credentials(api_key=api_key)  # credentials object to access GENAI


# Instantiate parameters for text generation
generate_params = GenerateParams(decoding_method="sample", max_new_tokens=5, min_new_tokens=1)
tokenize_params = TokenParams(return_tokens=True)


flan_ul2 = FlakyModel(ModelType.FLAN_UL2_20B, params=generate_params, credentials=creds)
prompts = ["Generate a random number > {}: ".format(i) for i in range(17)]
print("======== Async Generate with ordered=True ======== ")
counter = 0
for response in flan_ul2.generate_async(prompts, ordered=True):
    counter += 1
    if response is not None:
        print(counter, ":", response.input_text, " --> ", response.generated_text)
    else:
        print(counter, ":", None)

num_requests = 0

# Instantiate a model proxy object to send your requests
flan_ul2 = FlakyModel(ModelType.FLAN_UL2_20B, params=tokenize_params, credentials=creds)
prompts = ["Generate a random number > {}: ".format(i) for i in range(23)]
print("======== Async Tokenize with ordered=True ======== ")
counter = 0
for response in flan_ul2.tokenize_async(prompts, ordered=True):
    counter += 1
    if response is not None:
        print(counter, ":", response.input_text, " --> ", response.tokens)
    else:
        print(counter, ":", None)
