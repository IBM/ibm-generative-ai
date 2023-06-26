import pytest
from pydantic import ValidationError

from genai.schemas import GenerateParams, LengthPenalty, Return, ReturnOptions

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate


@pytest.mark.unit
class TestGenerateSchema:
    def setup_method(self):
        # mock object for the API call
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

        # test all GenerateParams fields
        self.params = GenerateParams(
            decoding_method="sample",
            length_penalty=LengthPenalty(decay_factor=1.5, start_index=2),
            max_new_tokens=3,
            min_new_tokens=1,
            random_seed=123,
            stop_sequences=["!", "?", "."],
            stream=False,
            temperature=0.5,
            time_limit=10.0,
            top_k=10,
            top_p=0.7,
            repetition_penalty=1.2,
            truncate_input_tokens=2,
            return_options=ReturnOptions(
                input_text=True,
                generated_tokens=True,
                input_tokens=True,
                token_logprobs=False,
            ),
        )

    @pytest.fixture
    def request_body(self):
        return {
            "model": self.model,
            "inputs": self.inputs,
            "params": self.params,
        }

    def test_existing_required_fields(self, request_body):
        assert "model" in request_body
        assert "inputs" in request_body

    def test_model(self, request_body):
        # test that the models list is not empty
        assert len(self.model) > 0
        # test that the models list contains only strings
        assert all(isinstance(model, str) for model in self.model)

    def test_inputs(self, request_body):
        # test that the inputs list is not empty
        assert len(self.inputs) > 0
        # test that the inputs list contains only strings
        assert all(isinstance(input, str) for input in self.inputs)

    def test_invalid_fields(self):
        # test generate invalid fields
        with pytest.raises(ValidationError):
            GenerateParams(
                decoding_method="invalid_method",
                length_penalty=LengthPenalty(decay_factor=0.5, start_index=-1),
                max_new_tokens=0,
                min_new_tokens=20,
                random_seed=10000,
                stop_sequences=[""],
                stream="false",
                temperature=-0.5,
                time_limit=-1.0,
                top_k=0,
                top_p=1.5,
                repetition_penalty=-0.5,
                truncate_input_tokens=-2.0,
                return_options=ReturnOptions(input_text="true", generated_tokens="false"),
            )

    def test_decoding_method_invalid_type(self):
        with pytest.raises(ValidationError):
            GenerateParams(decoding_method="invalid_method")

    def test_decoding_method_valid_type(self, request_body):
        # test that decoding_method must be either greedy or sample
        params = request_body["params"]
        assert params.decoding_method in ["greedy", "sample"]

    def test_max_new_tokens_invalid_type(self):
        # test that max_new_tokens must be an integer
        with pytest.raises(ValidationError):
            GenerateParams(max_new_tokens="3.5")
        with pytest.raises(ValidationError):
            GenerateParams(max_new_tokens="dummy")

    def test_max_new_token_valid_type(self, request_body):
        # test that max_new_tokens must be an intenger between 1 and 1024
        params = request_body["params"]
        assert params.max_new_tokens >= 1
        assert params.max_new_tokens <= 1024
        assert isinstance(params.max_new_tokens, int)

    def test_min_new_tokens_invalid_type(self):
        # test that min_new_tokens must be an integer
        with pytest.raises(ValidationError):
            GenerateParams(min_new_tokens="2.5")

    def test_min_new_tokens_valid_type(self, request_body):
        # test that min_new_tokens must be an integer and greater than 0
        # NOTE: min_new_tokens must be less than max_new_tokens?
        # NOTE: min_new_tokens can be 0?
        params = request_body["params"]
        assert params.min_new_tokens > 0
        assert isinstance(params.min_new_tokens, int)

    def test_random_seed_invalid_type(self):
        # test that random_seed must be an integer between 1 and 9999
        with pytest.raises(ValidationError):
            GenerateParams(random_seed="dummy")
        with pytest.raises(ValidationError):
            GenerateParams(random_seed=0)
        with pytest.raises(ValidationError):
            GenerateParams(random_seed=10000)

    def test_random_seed_valid_type(self, request_body):
        # test that random_seed must be an integer between 1 and 9999
        params = request_body["params"]
        assert params.random_seed >= 1
        assert params.random_seed <= 9999
        assert isinstance(params.random_seed, int)

    def test_stop_sequences_invalid_type(self):
        # test that stop_sequences must be a list of strings and not empty
        with pytest.raises(ValidationError):
            GenerateParams(stop_sequences=".")
        with pytest.raises(ValidationError):
            GenerateParams(stop_sequences=42)

    def test_stop_sequences_valid_type(self, request_body):
        # test that stop_sequences must be a list of strings and not empty
        params = request_body["params"]
        assert len(params.stop_sequences) > 0
        assert all(isinstance(stop, str) for stop in params.stop_sequences)

    def test_stream_invalid_type(self):
        # test that stream must be a boolean
        with pytest.raises(ValidationError):
            GenerateParams(stream="")
        with pytest.raises(ValidationError):
            GenerateParams(stream=[0, 1, 2])
        with pytest.raises(ValidationError):
            GenerateParams(stream="dummy")
        with pytest.raises(ValidationError):
            GenerateParams(stream=123)

    def test_stream_valid_type(self, request_body):
        # test that stream must be a boolean
        params = request_body["params"]
        assert isinstance(params.stream, bool)

    def test_temperature_invalid_type(self):
        # test that temperature must be a float between 0 and 1
        with pytest.raises(ValidationError):
            GenerateParams(temperature="")
        with pytest.raises(ValidationError):
            GenerateParams(temperature=[0, 1, 2])
        with pytest.raises(ValidationError):
            GenerateParams(temperature="dummy")
        with pytest.raises(ValidationError):
            GenerateParams(temperature=-0.5)
        with pytest.raises(ValidationError):
            GenerateParams(temperature=2.5)

    def test_temperature_valid_type(self, request_body):
        # test that temperature must be a float between 0 and 1
        params = request_body["params"]
        assert params.temperature >= 0
        assert params.temperature <= 2
        assert isinstance(params.temperature, float)

    def test_time_limit_invalid_type(self):
        # test that time_limit must be a int and greater than 0
        # NOTE: time_limit can be 0 or less then 0?
        with pytest.raises(ValidationError):
            GenerateParams(time_limit="")
        with pytest.raises(ValidationError):
            GenerateParams(time_limit=[0, 1, 2])
        with pytest.raises(ValidationError):
            GenerateParams(time_limit="dummy")

    def test_time_limit_valid_type(self, request_body):
        # test that time_limit must be a int
        params = request_body["params"]
        assert isinstance(params.time_limit, int)
        assert params.time_limit >= 0

    def test_top_k_invalid_type(self):
        # test that top_k must be an integer and greater than 0
        with pytest.raises(ValidationError):
            GenerateParams(top_k="")
        with pytest.raises(ValidationError):
            GenerateParams(top_k=[0, 1, 2])
        with pytest.raises(ValidationError):
            GenerateParams(top_k="dummy")
        with pytest.raises(ValidationError):
            GenerateParams(top_k=0.5)
        with pytest.raises(ValidationError):
            GenerateParams(top_k=0)

    def test_top_k_valid_type(self, request_body):
        # test that top_k must be an integer and greater than 0
        params = request_body["params"]
        assert isinstance(params.top_k, int)
        assert params.top_k > 0

    def test_top_p_invalid_type(self):
        # test that top_p must be a float between 0 and 1
        with pytest.raises(ValidationError):
            GenerateParams(top_p="")
        with pytest.raises(ValidationError):
            GenerateParams(top_p=[0, 1, 2])
        with pytest.raises(ValidationError):
            GenerateParams(top_p="dummy")
        with pytest.raises(ValidationError):
            GenerateParams(top_p=-0.5)
        with pytest.raises(ValidationError):
            GenerateParams(top_p=1.5)

    def test_top_p_valid_type(self, request_body):
        # test that top_p must be a float between 0 and 1
        params = request_body["params"]
        assert params.top_p >= 0
        assert params.top_p <= 1
        assert isinstance(params.top_p, float)

    def test_repetition_penalty_invalid_type(self):
        # test that repetition_penalty must be a float
        # NOTE: repetition_penalty can be 0 or less then 0?
        with pytest.raises(ValidationError):
            GenerateParams(repetition_penalty="")
        with pytest.raises(ValidationError):
            GenerateParams(repetition_penalty=[0, 1, 2])
        with pytest.raises(ValidationError):
            GenerateParams(repetition_penalty="dummy")

    def test_repetition_penalty_valid_type(self, request_body):
        # test that repetition_penalty must be a float
        params = request_body["params"]
        # assert params.repetition_penalty >= 0
        assert isinstance(params.repetition_penalty, float)

    def test_truncate_input_tokens_invalid_type(self):
        # test that truncate_input_tokens must be a interger
        with pytest.raises(ValidationError):
            GenerateParams(truncate_input_tokens="")
        with pytest.raises(ValidationError):
            GenerateParams(truncate_input_tokens=[0, 1, 2])
        with pytest.raises(ValidationError):
            GenerateParams(truncate_input_tokens="dummy")

    def test_truncate_input_tokens_valid_type(self, request_body):
        params = request_body["params"]
        assert isinstance(params.truncate_input_tokens, int)

    def test_returns_raises_warning(self):
        with pytest.deprecated_call():
            GenerateParams(returns=Return())
