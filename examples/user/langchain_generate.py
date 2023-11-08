import os
from typing import Any, Optional
from uuid import UUID

from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams
from genai.schemas.generate_params import HAPOptions, ModerationsOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)


class Callback(BaseCallbackHandler):
    def on_llm_new_token(
        self,
        token: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        print(f"Token received: {token}")


llm = LangChainInterface(
    model="google/flan-t5-xl",
    credentials=Credentials(api_key, api_endpoint),
    params=GenerateParams(
        decoding_method="sample",
        max_new_tokens=10,
        min_new_tokens=1,
        stream=True,
        temperature=0.5,
        top_k=50,
        top_p=1,
        moderations=ModerationsOptions(
            # Threshold is set to very low level to flag everything (testing purposes)
            # or set to True to enable HAP with default settings
            hap=HAPOptions(input=True, output=True, threshold=0.01)
        ),
    ),
)

result = llm.generate(
    prompts=["Tell me about IBM."],
    callbacks=[Callback()],
)
print(f"Response: {result.generations[0][0].text}")
print(result.llm_output)
print(result.generations[0][0].generation_info)
