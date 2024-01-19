"""
lm-evaluation-harness advanced usage

Use lm-evaluation extension from code to have additional control over concurrency or execution options

Note:
    This is for advanced usage only, use CLI in most cases (lm_eval_cli example)
"""

import logging
from pprint import pprint

from dotenv import load_dotenv
from lm_eval import simple_evaluate

from genai import Client, Credentials
from genai.extensions.lm_eval.model import IBMGenAILMEval
from genai.schema import TextGenerationParameters

load_dotenv()

logging.getLogger("httpx").setLevel(logging.WARN)
logging.getLogger("genai").setLevel(logging.WARN)

task_name = "arc_challenge"
model_id = "tiiuae/falcon-40b"
num_fewshot = 25
limit = 10  # WARNING: only for debug purposes, set None for full testing dataset

client = Client(
    credentials=Credentials.from_env(),
    config={"api_client_config": {"transport_options": {"retries": 999}}},
)
model = IBMGenAILMEval(
    client=client,
    model_id=model_id,
    show_progressbar=True,
    parameters=TextGenerationParameters(temperature=0),
)
results = simple_evaluate(model, tasks=[task_name], num_fewshot=num_fewshot, log_samples=False, limit=limit)

# add info about the model and few shot config
# "model_kwargs": model_kwargs,
results["config"] = {"model": model_id, "use_cache": False, "limit": limit, "model_kwargs": model.dump_parameters()}

pprint(results)
