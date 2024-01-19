import logging
import random
from pprint import pprint

import numpy as np
import torch
from dotenv import load_dotenv
from lm_eval import evaluate
from lm_eval.tasks import get_task_dict, initialize_tasks
from lm_eval.utils import eval_logger

from genai.extensions.lm_eval.model import IBMGenAILMEval

load_dotenv()

logging.getLogger("httpx").setLevel(logging.WARN)
logging.getLogger("genai").setLevel(logging.WARN)

initialize_tasks()

task_name = "arc_challenge"
model_id = "tiiuae/falcon-40b"
num_fewshot = 25
limit = 10  # WARNING: only for debug purposes, set None for full testing dataset

random.seed(0)
np.random.seed(1234)
torch.manual_seed(1234)  # TODO: this may affect training runs that are run with evaluation mid-run.

task_dict = get_task_dict([task_name])
for task_name in task_dict.keys():
    task = task_dict[task_name]
    task_config = task[1]._config if type(task) is tuple else task._config

    if task_config["num_fewshot"] == 0:
        eval_logger.info(f"num_fewshot has been set to 0 for {task_name} in its config. Manual configuration ignored.")
    else:
        default_val = task_config["num_fewshot"]
        eval_logger.warning(f"Overwriting default num_fewshot of {task_name} from {default_val} to {num_fewshot}")
        task_config["num_fewshot"] = num_fewshot

model = IBMGenAILMEval(model_id=model_id, show_progressbar=True)
results = evaluate(lm=model, task_dict=task_dict, log_samples=False, limit=limit)

# add info about the model and few shot config
# "model_kwargs": model_kwargs,
results["config"] = {"model": model_id, "use_cache": False, "limit": limit, "model_kwargs": model.dump_parameters()}

pprint(results)
