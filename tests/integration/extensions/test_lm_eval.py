import pytest
from dotenv import load_dotenv
from lm_eval.api.instance import Instance

from genai.extensions.lm_eval.model import IBMGenAILMEval
from genai.schema import DecodingMethod, TextGenerationParameters


@pytest.mark.integration
class TestLMEval:
    @pytest.fixture(autouse=True)
    def load_credentials(self):
        load_dotenv()

    def test_create_from_arg_string_raises_without_model_id(self):
        with pytest.raises(ValueError, match="'model_id' is required"):
            IBMGenAILMEval.create_from_arg_string("temperature=0")

    def test_create_from_arg_string(self):
        model = IBMGenAILMEval.create_from_arg_string(
            "model_id=google/flan-t5-xl,temperature=0,top_k=10,decoding_method=greedy,max_new_tokens=42"
        )
        assert model._parameters == TextGenerationParameters(
            temperature=0, top_k=10, decoding_method=DecodingMethod.GREEDY, max_new_tokens=42
        )

    @pytest.mark.vcr
    def test_loglikelihood_raises_for_invalid_tokenization(self):
        """Test loglikelihood of part of token is invalid"""
        lm = IBMGenAILMEval(model_id="tiiuae/falcon-40b")
        with pytest.raises(
            RuntimeError, match=r".*ends with a token .* that is substring of the continuation token .*"
        ):
            requests = [
                Instance(request_type="loglikelihood", doc=args, arguments=args, idx=i)
                for i, args in enumerate([("test str", "ing")])
            ]
            lm.loglikelihood(requests)

    @pytest.mark.vcr
    def test_loglikelihood(self):
        """Test loglikelihood of part of token is invalid"""
        lm = IBMGenAILMEval(model_id="tiiuae/falcon-40b")
        requests = [
            Instance(request_type="loglikelihood", doc=args, arguments=args, idx=i)
            for i, args in enumerate(
                [
                    (
                        "Classify the following tweet: 'No this is my first job' "
                        "into 'complaint' or 'no complaint':",
                        "no complaint",
                    ),
                    (
                        "Classify the following tweet: 'Please just give me my money back.' "
                        "into 'complaint' or 'no complaint':",
                        "complaint",
                    ),
                ]
            )
        ]
        results = lm.loglikelihood(requests)
        assert len(results) == 2
        assert results[0].log_likelihood < 0, results[1].log_likelihood < 0

    @pytest.mark.vcr
    def test_generate_until(self):
        lm = IBMGenAILMEval(model_id="google/flan-t5-xl")
        requests = [
            Instance(request_type="loglikelihood", doc=args, arguments=args, idx=i)
            for i, args in enumerate(
                [
                    (
                        "Here are three sentences. My favorite color is ",
                        {"temperature": 1, "max_gen_toks": 1000, "until": "."},
                    ),
                    (
                        "Here are three sentences. I'm happy because ",
                        {"temperature": 0, "max_gen_toks": 1000, "until": "."},
                    ),
                    (
                        "Here are three sentences. When I'm bored, I ",
                        {"temperature": 1, "max_gen_toks": 1000, "until": "."},
                    ),
                ]
            )
        ]
        results = lm.generate_until(requests)
        assert len(results) == 3
        assert {result[-1] for result in results} == {"."}
