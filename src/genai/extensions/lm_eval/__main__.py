import logging
import signal

from genai import handle_shutdown_event
from genai.extensions.lm_eval.model import initialize_model

try:
    # load dotenv if installed
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    ...


try:
    from lm_eval.__main__ import cli_evaluate
except ImportError:
    raise ImportError("Could not import lm_eval: Please install ibm-generative-ai[lm-eval] extension.")  # noqa: B904


initialize_model()

signal.signal(signal.SIGINT, handle_shutdown_event)
signal.signal(signal.SIGTERM, handle_shutdown_event)

logging.getLogger("httpx").setLevel(logging.WARN)
logging.getLogger("genai").setLevel(logging.WARN)

cli_evaluate()
