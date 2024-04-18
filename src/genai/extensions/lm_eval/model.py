import json
from collections import defaultdict
from functools import cached_property
from typing import Any, Iterator, NamedTuple, Optional, Type, cast

from genai import Client, Credentials
from genai.schema import (
    BaseTokens,
    DecodingMethod,
    TextGenerationParameters,
    TextGenerationReturnOptions,
    TextTokenizationParameters,
    TextTokenizationReturnOptions,
)
from genai.text.generation import CreateExecutionOptions as TextGenerationExecutionOptions
from genai.text.tokenization import CreateExecutionOptions as TokenizationExecutionOptions

try:
    import lm_eval.utils
    from lm_eval.api.instance import Instance
    from lm_eval.api.model import LM
    from lm_eval.api.registry import register_model
    from lm_eval.models.utils import Grouper
except ImportError:
    raise ImportError("Could not import lm_eval: Please install ibm-generative-ai[lm-eval] extension.")  # noqa: B904
try:
    from tqdm import tqdm
except ImportError:
    raise ImportError("Could not import tqdm: Please install ibm-generative-ai[lm-eval] extension.")  # noqa: B904


class LogLikelihoodResult(NamedTuple):
    log_likelihood: float
    is_greedy: bool


def initialize_model():
    pass  # model is registered by importing this module


@register_model("ibm_genai")
class IBMGenAILMEval(LM):
    """
    Implementation of LM model interface for evaluating GenAI model with the lm_eval framework.

    See https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/model_guide.md for reference.
    """

    DEFAULT_TOKENIZATION_EXECUTION_OPTIONS = TokenizationExecutionOptions(
        batch_size=100,
        concurrency_limit=5,
    )
    DEFAULT_GENERATION_EXECUTION_OPTIONS = TextGenerationExecutionOptions()
    DEFAULT_NUM_RETRIES = 6  # Increased number of retries for robustness, because evaluation typically runs for hours

    @classmethod
    def create_from_arg_string(
        cls: Type["IBMGenAILMEval"],
        arg_string: str,
        additional_config: Optional[dict] = None,
    ) -> "IBMGenAILMEval":
        """Allow the user to specify model parameters (TextGenerationParameters) in CLI arguments."""
        additional_config = {} if additional_config is None else additional_config
        args = lm_eval.utils.simple_parse_args_string(arg_string)
        model_id = args.pop("model_id", None)
        if model_id is None:
            raise ValueError("'model_id' is required, please pass it in 'model_args'")
        parameters = TextGenerationParameters.model_validate(args)
        return cls(client=Client(credentials=Credentials.from_env()), model_id=model_id, parameters=parameters)

    def __init__(
        self,
        client: Optional[Client] = None,
        model_id: Optional[str] = None,
        parameters: Optional[TextGenerationParameters] = None,
        show_progressbar: Optional[bool] = True,
        tokenization_execution_options: Optional[TokenizationExecutionOptions] = None,
        generation_execution_options: Optional[TextGenerationExecutionOptions] = None,
    ):
        super().__init__()
        self._client = client or Client(
            credentials=Credentials.from_env(),
            config={"api_client_config": {"transport_options": {"retries": self.DEFAULT_NUM_RETRIES}}},
        )
        self._model_id = model_id
        self._parameters = parameters or TextGenerationParameters()
        self._show_progressbar = show_progressbar

        for opts, name in [
            (tokenization_execution_options, "tokenization"),
            (generation_execution_options, "generation"),
        ]:
            if opts and opts.ordered is False:
                raise ValueError(f"Ordering is not configurable for evaluation ({name}_execution_options).")

        self._tokenization_execution_options = (
            tokenization_execution_options or self.DEFAULT_TOKENIZATION_EXECUTION_OPTIONS
        )
        self._generation_execution_options = generation_execution_options or self.DEFAULT_GENERATION_EXECUTION_OPTIONS

    @cached_property
    def model_token_limit(self):
        return self._client.model.retrieve(id=self._model_id).result.token_limits[0].token_limit

    def dump_parameters(self):
        return self._parameters.model_dump()

    def _tokenize(self, inputs: list[str]) -> Iterator[list[str]]:
        pb = tqdm(desc="Tokenizing requests", total=len(inputs), disable=not self._show_progressbar)
        for response in self._client.text.tokenization.create(
            model_id=self._model_id,
            input=inputs,
            parameters=TextTokenizationParameters(return_options=TextTokenizationReturnOptions(tokens=True)),
            execution_options=self._tokenization_execution_options,
        ):
            pb.update(len(response.results))
            for result in response.results:
                yield result.tokens
        pb.close()

    def _check_last_token_is_stop_token(self, response_tokens: list[str], context_tokens: list[str]) -> bool:
        """
        Check whether tokens from context and response are the same.
        Only last token can differ, in case or stop sequence (</s>)

        Returns:
            True if only last token differs, False if all tokens are the same
        Raises:
            RuntimeError: if some other tokens differ than the last one
            RuntimeError: if last token differs but context token is substring of response token.
                Loglikelihood of second part of token is not defined

        """
        context_length = len(context_tokens)
        if response_tokens[: context_length - 1] != context_tokens[: context_length - 1]:
            raise RuntimeError(
                f"There is an unexpected difference between tokenizer and model tokens:\n"
                f"context_tokens={context_tokens}\n"
                f"response_tokens={response_tokens[:context_length]}"
            )

        last_context_token = context_tokens[context_length - 1]
        last_context_token_resp = response_tokens[context_length - 1]
        if last_context_token != last_context_token_resp and last_context_token_resp.startswith(last_context_token):
            raise RuntimeError(
                f"The context sent to loglikelihood evaluation ends with a token ({last_context_token}) "
                f"that is substring of the continuation token ({last_context_token_resp}).\n"
                f"context_tokens={context_tokens}\n"
                f"response_tokens={response_tokens[:context_length]}\n"
                "This is not allowed as it would skew the results. Please check your data."
            )
        return last_context_token != last_context_token_resp

    def _check_model_logprobs_support(self):
        input_tokens = (
            list(
                self._client.text.generation.create(
                    model_id=self._model_id,
                    inputs=["The best ice cream flavor is:"],
                    parameters=self._log_likelihood_parameters,
                    execution_options=self._generation_execution_options,
                )
            )[0]
            .results[0]
            .input_tokens
        )

        if all(token.logprob is None for token in input_tokens):
            raise RuntimeError(f"Model {self._model_id} is not supported: does not return logprobs for input tokens")

    def _get_log_likelihood(self, input_tokens: list[BaseTokens], context_tokens: list[str]) -> LogLikelihoodResult:
        response_tokens: list[str] = [token.text for token in input_tokens]
        context_length = len(context_tokens)

        if self._check_last_token_is_stop_token(response_tokens, context_tokens):
            context_length -= 1

        return LogLikelihoodResult(
            log_likelihood=sum(token.logprob for token in input_tokens[context_length:]),
            is_greedy=all(token.rank == 1 for token in input_tokens[context_length:]),
        )

    @property
    def _log_likelihood_parameters(self):
        return TextGenerationParameters.model_validate(
            {
                **self._parameters.model_dump(),
                "max_new_tokens": 1,  # 0 is treated like "unlimited"
                "return_options": TextGenerationReturnOptions(
                    input_tokens=True,
                    token_logprobs=True,
                    token_ranks=True,
                ),
            }
        )

    def loglikelihood(self, requests: list[Instance]) -> list[tuple[float, bool]]:
        """
        Args:
            requests: Each request contains Instance.args : Tuple[str, str] containing:
                1. an input string to the LM and
                2. a target string on which the loglikelihood of the LM producing this target,
                   conditioned on the input, will be returned.
        Returns:
            tuple (loglikelihood, is_greedy) for each request according to the input order:
                loglikelihood: probability of generating the target string conditioned on the input
                is_greedy: True if and only if the target string would be generated by greedy sampling from the LM
        """
        self._check_model_logprobs_support()

        requests = [request.args for request in requests]
        results: list[LogLikelihoodResult] = []

        contexts_tokenized = list(self._tokenize([context for context, _ in requests]))
        generation_inputs = [context + continuation for context, continuation in requests]

        pb = tqdm(desc="Running text generation", total=len(contexts_tokenized), disable=not self._show_progressbar)
        for response, context_tokens in zip(
            self._client.text.generation.create(
                model_id=self._model_id,
                inputs=generation_inputs,
                parameters=self._log_likelihood_parameters,
                execution_options=self._generation_execution_options,
            ),
            contexts_tokenized,
        ):
            pb.update(len(response.results))
            for result in response.results:
                results.append(self._get_log_likelihood(result.input_tokens, context_tokens))
        pb.close()
        return cast(list[tuple[float, bool]], results)

    def loglikelihood_rolling(self, requests: list[Instance]) -> list[tuple[float, bool]]:
        """
        Used to evaluate perplexity on a data distribution.

        Args:
            requests: Each request contains Instance.args : tuple[str] containing an input string to the model whose
                entire loglikelihood, conditioned on purely the EOT token, will be calculated.
        Returns:
            tuple (loglikelihood,) for each request according to the input order:
                loglikelihood: solely the probability of producing each piece of text given no starting input.
        """

        self._check_model_logprobs_support()

        generation_inputs = [request.args[0] for request in requests]
        results: list[LogLikelihoodResult] = []
        for response in zip(
            self._client.text.generation.create(
                model_id=self._model_id,
                inputs=generation_inputs,
                parameters=self._log_likelihood_parameters,
                execution_options=self._generation_execution_options,
            ),
        ):
            for result in response.results:
                results.append(self._get_log_likelihood(result.input_tokens, []))

        return cast(list[tuple[float, bool]], results)

    def generate_until(self, requests: list[Instance]) -> list[str]:
        """
        From official model_guide: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/model_guide.md:

        Each request contains Instance.args : Tuple[str, dict] containing:
            1. an input string to the LM and
            2. a dictionary of keyword arguments used to control generation parameters.
        Using this input and these generation parameters, text will be sampled from the language model

        (
            typically until a maximum output length or specific stopping string sequences--for example,
            {"until": ["\n\n", "."], "max_gen_toks": 128}
        ).
        The generated input+output text from the model will then be returned.
        """
        # group requests by their args (e.g. temperature, do_sample, etc.)
        grouper = Grouper(requests, lambda request: json.dumps(request.args[1], sort_keys=True))
        results: dict[str, list[str]] = defaultdict(list)

        pb = tqdm(desc="Running text generation", total=len(requests), disable=not self._show_progressbar)

        for key, requests_group in grouper.get_grouped().items():
            generation_parameters: dict[str, Any] = requests_group[0].args[1]
            inputs = [request.args[0] for request in requests_group]

            # Process parameters
            do_sample = generation_parameters.pop("do_sample", False)
            decoding_method = DecodingMethod.SAMPLE if do_sample else DecodingMethod.GREEDY
            until = generation_parameters.pop("until")
            stop_sequences = [until] if isinstance(until, str) else until
            stop_sequences.append("<|endoftext|>")
            # Use same default 256 token limit as huggingface
            # https://github.com/EleutherAI/lm-evaluation-harness/blob/7852985b2b5352df147067e01a121c52297f8821/lm_eval/models/huggingface.py#L392
            max_new_tokens = generation_parameters.pop("max_gen_toks", 256)
            temperature = generation_parameters.pop("temperature", None)
            truncate_input_tokens = self.model_token_limit - max_new_tokens

            parameters = TextGenerationParameters.model_validate(
                {
                    **self._parameters.model_dump(),
                    "decoding_method": decoding_method,
                    "stop_sequences": stop_sequences,
                    "temperature": temperature,
                    "max_new_tokens": max_new_tokens,
                    "truncate_input_tokens": truncate_input_tokens,
                }
            )

            for response in self._client.text.generation.create(
                model_id=self._model_id, inputs=inputs, parameters=parameters
            ):
                results[key].extend(result.generated_text for result in response.results)
                pb.update(len(response.results))

        pb.close()

        return grouper.get_original(results)
