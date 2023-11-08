import os

from dotenv import load_dotenv
from langchain.evaluation import EvaluatorType, load_evaluator

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainChatInterface
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
credentials = Credentials(api_key, api_endpoint=api_endpoint)

# Load a trajectory (conversation) evaluator
llm = LangChainChatInterface(
    model="meta-llama/llama-2-70b-chat",
    credentials=credentials,
    params=GenerateParams(
        decoding_method="sample",
        min_new_tokens=1,
        max_new_tokens=100,
        length_penalty={
            "decay_factor": 1.5,
            "start_index": 50,
        },
        temperature=1.2,
        stop_sequences=["<|endoftext|>", "}]"],
    ),
)
evaluator = load_evaluator(evaluator=EvaluatorType.AGENT_TRAJECTORY, llm=llm)
print(evaluator)
