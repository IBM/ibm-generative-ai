import os, logging
from dotenv import load_dotenv

# from genai.extensions.langchain import LangChainInterface

try:
    from genai.extensions.langchain import WatsonX
except ImportError:
    raise ImportError('Could not import WatsonX')


## source https://python.langchain.com/docs/use_cases/question_answering

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Load documents

from langchain.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")

# Split documents
logger.info(f'web loader is loading content ...')
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
splits = text_splitter.split_documents(loader.load())

# Embed and store splits
logger.info(f'vector soter is populating ...')
from langchain.vectorstores import Chroma
#from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings
vectorstore = Chroma.from_documents(documents=splits,embedding=SentenceTransformerEmbeddings())
retriever = vectorstore.as_retriever()

question = "What are the approaches to Task Decomposition?"
docs = vectorstore.similarity_search(question)
logger.info(f'len(docs) = {len(docs)}')

# Prompt 
# https://smith.langchain.com/hub/rlm/rag-prompt

from langchain import hub

## for https://smith.langchain.com
langChain_api_key = os.getenv("LangChain_API_KEY", None)

rag_prompt = hub.pull("rlm/rag-prompt", api_key=langChain_api_key)

logger.info(f'rag_prompt = {rag_prompt}\n')
# LLM


# llm = Model("ibm/falcon-40b-8lang-instruct", params=params, credentials=creds)

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

model_kwargs = {
    "decoding_method": "greedy",
    "max_new_tokens": 200,
    "min_new_tokens": 1,
    "stream": False,
    "temperature": 0.7,
    "repetition_penalty": 1.0,
    "top_k": 50,
    "top_p": 1,
}

llm = WatsonX(
    model_name="ibm/falcon-40b-8lang-instruct", 
    model_kwargs=model_kwargs,
    watsonx_api_key=api_key,
    watsonx_api_base=api_endpoint,
    verbose=True
    )
        
from langchain.retrievers.multi_query import MultiQueryRetriever

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

retriever_from_llm = MultiQueryRetriever.from_llm(retriever=vectorstore.as_retriever(),
                                                  llm=llm)
unique_docs = retriever_from_llm.get_relevant_documents(query=question)
len(unique_docs)

# RAG chain 

from langchain.schema.runnable import RunnablePassthrough
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} 
    | rag_prompt 
    | llm 
)

msg = rag_chain.invoke("What is Task Decomposition?")
print(f'invork msg = {msg}')
