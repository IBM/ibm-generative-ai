"""Chat with a model using LangChain"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from genai import Client, Credentials
from genai.extensions.langchain.chat_llm import LangChainChatInterface
from genai.text.generation import (
    DecodingMethod,
    ModerationHAP,
    ModerationParameters,
    TextGenerationParameters,
    TextGenerationReturnOptions,
)

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


llm = LangChainChatInterface(
    client=Client(credentials=Credentials.from_env()),
    model_id="meta-llama/llama-2-70b-chat",
    parameters=TextGenerationParameters(
        decoding_method=DecodingMethod.SAMPLE,
        max_new_tokens=100,
        min_new_tokens=10,
        temperature=0.5,
        top_k=50,
        top_p=1,
        return_options=TextGenerationReturnOptions(input_text=False, input_tokens=True),
    ),
    moderations=ModerationParameters(
        # Threshold is set to very low level to flag everything (testing purposes)
        # or set to True to enable HAP with default settings
        hap=ModerationHAP(input=True, output=False, threshold=0.01)
    ),
)

print(heading("Start conversation with langchain"))
prompt = "Describe what is Python in one sentence."
print(f"Request: {prompt}")
result = llm.generate(
    messages=[
        [
            SystemMessage(
                content="""You are a helpful, respectful and honest assistant.
Always answer as helpfully as possible, while being safe.
Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.
Please ensure that your responses are socially unbiased and positive in nature. If a question does not make
any sense, or is not factually coherent, explain why instead of answering something incorrectly.
If you don't know the answer to a question, please don't share false information.
""",
            ),
            HumanMessage(content=prompt),
        ]
    ],
)
conversation_id = result.generations[0][0].generation_info["meta"]["conversation_id"]
print(f"New conversation with ID '{conversation_id}' has been created!")
print(f"Response: {result.generations[0][0].text}")
print(result.llm_output)
print(result.generations[0][0].generation_info)

print(heading("Continue conversation with langchain"))
prompt = "Show me some simple code example."
print(f"Request: {prompt}")
result = llm.generate(
    messages=[[HumanMessage(content=prompt)]], conversation_id=conversation_id, use_conversation_parameters=True
)
print(f"Response: {result.generations[0][0].text}")
