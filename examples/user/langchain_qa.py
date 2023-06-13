import os

from dotenv import load_dotenv

try:
    from langchain import PromptTemplate
    from langchain.chains import LLMChain, SimpleSequentialChain
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams, ModelType

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
).dict()  # Langchain uses dictionaries to pass kwargs

pt1 = PromptTemplate(input_variables=["topic"], template="Generate a random question about {topic}: Question: ")
pt2 = PromptTemplate(
    input_variables=["question"],
    template="Answer the following question: {question}",
)


creds = Credentials(api_key, api_endpoint)
flan = LangChainInterface(model=ModelType.FLAN_UL2, credentials=creds, params=params)
model = LangChainInterface(model=ModelType.FLAN_UL2, credentials=creds)
prompt_to_flan = LLMChain(llm=flan, prompt=pt1)
flan_to_model = LLMChain(llm=model, prompt=pt2)
qa = SimpleSequentialChain(chains=[prompt_to_flan, flan_to_model], verbose=True)
qa.run("life")
