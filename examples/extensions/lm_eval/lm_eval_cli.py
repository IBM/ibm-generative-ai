"""
lm-evaluation-harness CLI usage

The recommended way to run benchmarks is through CLI.
In your python environment with 'ibm-generative-ai[lm-eval]' installed:

Example::

    python -m genai.extensions.lm_eval \\
          --model="ibm_genai" \\
          --model_args="model_id=mistralai/mixtral-8x7b-instruct-v01,temperature=0" \\
          --task="hellaswag" \\
          --num_fewshot=10 \\
          --output_path="falcon-40b_hellaswag.json"
"""

import subprocess

subprocess.run(
    [
        "python",
        "-m",
        "genai.extensions.lm_eval",
        "--model=ibm_genai",
        "--model_args=model_id=mistralai/mixtral-8x7b-instruct-v01,temperature=0",
        "--task=hellaswag",
        "--num_fewshot=10",
        "--limit=10",  # WARNING: only for debug purposes, remove for full testing dataset
    ],
    check=True,
    text=True,
    capture_output=False,
)
