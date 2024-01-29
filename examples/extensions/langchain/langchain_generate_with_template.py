"""Use LangChain generation with a custom template."""

from dotenv import load_dotenv

from genai import Client, Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schema import TextGenerationParameters, TextGenerationReturnOptions

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

prompt_response = client.prompt.create(
    name="Recipe Generator Prompt",
    model_id="google/flan-t5-xl",
    input="Make a short recipe for {{meal}} (use bullet points)",
)

try:
    llm = LangChainInterface(
        client=client,
        model_id="ibm/granite-13b-instruct-v2",
        prompt_id=prompt_response.result.id,
        parameters=TextGenerationParameters(
            min_new_tokens=100,
            max_new_tokens=500,
            return_options=TextGenerationReturnOptions(input_text=False, input_tokens=True),
        ),
        data={"meal": "Lasagne"},
    )
    for chunk in llm.stream(""):
        print(chunk, end="")
finally:
    # Delete the prompt if you don't need it
    client.prompt.delete(prompt_response.result.id)
