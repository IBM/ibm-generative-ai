"""Text generation using LangChain"""

from typing import Any, Optional
from uuid import UUID

from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler

from genai import Client, Credentials
from genai.extensions.langchain import LangChainInterface
from genai.text.generation import (
    DecodingMethod,
    ModerationHAP,
    ModerationParameters,
    TextGenerationParameters,
)

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


print(heading("Generate text with langchain"))


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
    model_id="google/flan-t5-xl",
    client=Client(credentials=Credentials.from_env()),
    parameters=TextGenerationParameters(
        decoding_method=DecodingMethod.SAMPLE,
        max_new_tokens=10,
        min_new_tokens=1,
        temperature=0.5,
        top_k=50,
        top_p=1,
    ),
    moderations=ModerationParameters(
        # Threshold is set to very low level to flag everything (testing purposes)
        # or set to True to enable HAP with default settings
        hap=ModerationHAP(input=True, output=True, threshold=0.01)
    ),
)

prompt = "Tell me about IBM."
print(f"Prompt: {prompt}")

result = llm.generate(prompts=[prompt], callbacks=[Callback()])

print(f"Answer: {result.generations[0][0].text}")
print(result.llm_output)
print(result.generations[0][0].generation_info)
