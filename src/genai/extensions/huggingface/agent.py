import logging

try:
    from transformers import Agent
except ImportError:
    raise ImportError(
        "Could not import HuggingFace transformers: Please install ibm-generative-ai[huggingface] extension."
    )


from typing import List, Optional

from genai import Credentials, Model
from genai.schemas import GenerateParams

logger = logging.getLogger(__name__)


class IBMGenAIAgent(Agent):
    def __init__(
        self,
        credentials: Credentials = None,
        model: Optional[str] = None,
        params: Optional[GenerateParams] = None,
        chat_prompt_template: Optional[str] = None,
        run_prompt_template: Optional[str] = None,
        additional_tools: Optional[List[str]] = None,
    ):
        super().__init__(
            chat_prompt_template=chat_prompt_template,
            run_prompt_template=run_prompt_template,
            additional_tools=additional_tools,
        )
        self.credentials = credentials
        self.model = model
        self.params = params

    def generate_one(self, prompt, stop):
        return self._generate([prompt], stop)[0]

    def generate_many(self, prompts, stop):
        return self._generate(prompts, stop)

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> List[str]:
        result: List[str] = []
        if len(prompts) == 0:
            return result

        params = self._get_params()
        params.stop_sequences = stop or params.stop_sequences
        model = Model(model=self.model, params=params, credentials=self.credentials)
        for response in model.generate(prompts=prompts):
            generated_text = response.generated_text

            logger.info("Output of GENAI call: {}".format(generated_text))
            result.append(generated_text)

        return result

    def _get_params(self):
        if self.params is None:
            return GenerateParams()

        if isinstance(self.params, dict):
            return GenerateParams(**self.params)
        return self.params.copy()
