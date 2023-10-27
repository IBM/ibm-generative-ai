import os, logging
from dotenv import load_dotenv

from genai.extensions.langchain import WatsonX

## source https://python.langchain.com/docs/use_cases/question_answering/code_understanding

## Loading
from git import Repo
from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Clone
repo_path = "/root/jupyter/test/test_repo/langchain"
data_root = "/root/jupyter/test/data/rag"

dataset = 'LangChain'
data_dir = os.path.join(data_root, dataset)
max_docs = -1

if os.path.exists(os.path.join(repo_path, 'docs')):
    pass
else:
    logger.info(f'clone in to {repo_path}')
    # os.rmdir(repo_path)
    repo = Repo.clone_from("https://github.com/langchain-ai/langchain", to_path=repo_path)

# Load
loader = GenericLoader.from_filesystem(
    repo_path+"/libs/test/langchain",
    glob="**/*",
    suffixes=[".py"],
    parser=LanguageParser(language=Language.PYTHON, parser_threshold=500)
)
documents = loader.load()

print(f'len(documents) = {len(documents)}')
logger.info(f'len(documents) = {len(documents)}')

## Splitting

from langchain.text_splitter import RecursiveCharacterTextSplitter
python_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, 
                                                               chunk_size=2000, 
                                                               chunk_overlap=200)
texts = python_splitter.split_documents(documents)
len(texts)

## RetrievalQA


from langchain.vectorstores import Chroma

# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings

if os.path.exists(data_dir):
    logger.info(f'load chroma vectors from {data_dir}')
    db = Chroma(
        embedding_function=SentenceTransformerEmbeddings(),
        persist_directory=data_dir
    )
else:
    logger.info(f'It takes long time to populate Chroma db. Please be patient ...')
    db = Chroma.from_documents(
        texts, 
        SentenceTransformerEmbeddings(),
        persist_directory=data_dir)
    

retriever = db.as_retriever(
    search_type="mmr", # Also test "similarity"
    search_kwargs={"k": 8},
)

## Chat

from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain

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

memory = ConversationSummaryMemory(llm=llm,memory_key="chat_history",return_messages=True)
qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)

question = "How can I initialize a ReAct agent?"
print(f'question = {question}')
logger.info(f'question = {question}')
result = qa(question)
logger.info(f'result["answer"] = {result["answer"]}')

questions = [
    "What is the class hierarchy?",
    "What classes are derived from the Chain class?",
    "What one improvement do you propose in code in relation to the class hierarchy for the Chain class?",
]

for question in questions:
    result = qa(question)
    print(f"-> **Question**: {question} \n")
    print(f"**Answer**: {result['answer']} \n")


output = '''
-> **Question**: What is the class hierarchy?

**Answer**:  (superclass, subclass, etc.)

-> **Question**: What classes are derived from the Chain class?

**Answer**:
Answer not in context

-> **Question**: What one improvement do you propose in code in relation to the class hierarchy for the Chain class?

**Answer**:

The Chain class is a generic class that can be used to represent a chain of other classes. It is not specific to any particular application domain.
'''