"""QA using native LangChain features"""

from dotenv import load_dotenv

from genai import Client, Credentials
from genai.extensions.langchain import LangChainInterface
from genai.text.generation import DecodingMethod, TextGenerationParameters

try:
    from langchain.prompts import PromptTemplate
    from langchain.schema import StrOutputParser
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


print(heading("QA with Langchain"))

parameters = TextGenerationParameters(
    decoding_method=DecodingMethod.SAMPLE,
    max_new_tokens=100,
    min_new_tokens=1,
    temperature=0.5,
    top_k=50,
    top_p=1,
)

pt1 = PromptTemplate(
    input_variables=["topic"],
    template="Generate a random question about {topic}: Question: ",
)
pt2 = PromptTemplate(
    input_variables=["question"],
    template="Answer the following question: {question}",
)


client = Client(credentials=Credentials.from_env())
model_id = "google/flan-ul2"
flan = LangChainInterface(model_id=model_id, client=client, parameters=parameters)
model = LangChainInterface(model_id=model_id, client=client)

prompt_to_flan_chain = pt1 | flan | StrOutputParser()
flan_to_model_chain = pt2 | model | StrOutputParser()

chain = {"question": prompt_to_flan_chain} | flan_to_model_chain
print(chain.invoke({"topic": "life"}))
