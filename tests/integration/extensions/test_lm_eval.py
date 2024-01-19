import pytest
from lm_eval.api.instance import Instance

from genai import Client
from genai.extensions.lm_eval.model import IBMGenAILMEval


@pytest.mark.integration
class TestLMEval:
    def test_agent(self, client: Client):
        model = "meta-llama/llama-2-70b"
        model = IBMGenAILMEval(client=client, model_id=model)
        likelihood_response = model.loglikelihood(
            [
                Instance(
                    request_type="loglikelihood",
                    arguments=("Hello, how are", "you?"),
                    idx=0,
                    doc={},
                )
            ]
        )
        # TODO: wip
        assert likelihood_response
