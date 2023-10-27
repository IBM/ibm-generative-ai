import os

from dotenv import load_dotenv

try:
    from langchain.prompts import PromptTemplate
    from langchain.schema import StrOutputParser
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=100,
    min_new_tokens=1,
    stream=False,
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


creds = Credentials(api_key, api_endpoint)
flan = LangChainInterface(model="google/flan-ul2", credentials=creds, params=params)
model = LangChainInterface(model="google/flan-ul2", credentials=creds)

prompt_to_flan_chain = pt1 | flan | StrOutputParser()
flan_to_model_chain = pt2 | model | StrOutputParser()

chain = {"question": prompt_to_flan_chain} | flan_to_model_chain
print(chain.invoke({"topic": "life"}))
