import logging

try:
    from transformers import Agent
except ImportError:
    raise ImportError(  # noqa: B904
        "Could not import HuggingFace transformers: Please install ibm-generative-ai[huggingface] extension."
    )


from typing import List, Optional

from genai._utils.general import to_model_instance
from genai.client import Client
from genai.schema import TextGenerationParameters

logger = logging.getLogger(__name__)


class IBMGenAIAgent(Agent):
    def __init__(
        self,
        client: Client,
        model: Optional[str] = None,
        parameters: Optional[TextGenerationParameters] = None,
        chat_prompt_template: Optional[str] = None,
        run_prompt_template: Optional[str] = None,
        additional_tools: Optional[List[str]] = None,
    ):
        super().__init__(
            chat_prompt_template=chat_prompt_template,
            run_prompt_template=run_prompt_template,
            additional_tools=additional_tools,
        )
        self.client = client
        self.model = model
        self.parameters = parameters

    def generate_one(self, prompt, stop):
        return self._generate([prompt], stop)[0]

    def generate_many(self, prompts, stop):
        return self._generate(prompts, stop)

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> List[str]:
        final_results: List[str] = []
        if len(prompts) == 0:
            return final_results

        params = to_model_instance(self.parameters, TextGenerationParameters)
        params.stop_sequences = stop or params.stop_sequences
        for response in self.client.text.generation.create(model_id=self.model, inputs=prompts, parameters=params):
            for result in response.results:
                generated_text = result.generated_text or ""

                logger.info("Output of GENAI call: {}".format(generated_text))
                final_results.append(generated_text)

        return final_results
