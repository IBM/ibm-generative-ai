import pytest
from pytest_httpx import HTTPXMock

from genai import Credentials, Model
from genai.exceptions import GenAiException
from genai.routers import TunesRouter
from genai.schemas import GenerateParams
from genai.schemas.responses import (
    GenerateResponse,
    ModelCard,
    ModelList,
    TokenizeResponse,
)
from genai.schemas.tunes_params import CreateTuneHyperParams
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint


@pytest.mark.unit
class TestModel:
    def setup_method(self):
        self.creds = Credentials(api_key="API_KEY")
        self.service = ServiceInterface(service_url="http://service_url", api_key="API_KEY")
        self.model = "google/flan-ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def params(self):
        return GenerateParams(
            decoding_method="sample",
            max_new_tokens=1,
            min_new_tokens=1,
            stream=False,
            temperature=0.7,
            top_k=50,
            top_p=1,
        )

    @pytest.fixture
    def prompts(self):
        return ["a", "b", "c", "d", "e"]

    def test_generate(self, credentials, params, prompts, httpx_mock: HTTPXMock):
        """Tests that we can call the generate endpoint"""

        GENERATE_RESPONSE = SimpleResponse.generate(model="google/flan-ul2", inputs=prompts, params=params)
        expected_generated_response = GenerateResponse(**GENERATE_RESPONSE)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", json=GENERATE_RESPONSE)

        model = Model("google/flan-ul2", params=params, credentials=credentials)

        responses = model.generate_as_completed(prompts=prompts)
        responses_list = list(responses)

        assert responses_list == expected_generated_response.results
        for i, response in enumerate(responses_list):
            assert response.input_text == prompts[i]

    def test_generate_throws_exception_for_non_200(self, credentials, params, prompts, httpx_mock: HTTPXMock):
        """Tests that the GenAiException is thrown if the status code is not 200"""

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.GENERATE), method="POST", status_code=500)

        model = Model("google/flan-ul2", params=params, credentials=credentials)

        with pytest.raises(GenAiException):
            model.generate(prompts=prompts)

    def test_generate_throws_exception_for_generic_exception(self, credentials, params, prompts, httpx_mock: HTTPXMock):
        """Tests that the GenAiException is thrown if a generic Exception is raised"""
        httpx_mock.add_exception(("some general error"))
        model = Model("google/flan-ul2", params=params, credentials=credentials)

        with pytest.raises(GenAiException):
            model.generate(prompts=prompts)

    def test_tokenize(self, credentials, params, httpx_mock: HTTPXMock):
        """Tests that we can call the tokenize endpoint"""

        TOKENIZE_RESPONSE = SimpleResponse.tokenize(model="google/flan-ul2", inputs=["a", "b", "c"])
        expected_token_response = TokenizeResponse(**TOKENIZE_RESPONSE)

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.TOKENIZE), method="POST", json=TOKENIZE_RESPONSE)

        model = Model("google/flan-ul2", params=params, credentials=credentials)

        responses = model.tokenize(["a", "b", "c"], False)

        assert responses == expected_token_response.results

    def test_create_tune(self, credentials, httpx_mock: HTTPXMock):
        label = "test_label"
        model_id = self.model
        hyperparams = CreateTuneHyperParams(num_epochs=10)
        expected_response = SimpleResponse.create_tune(model_id=model_id, name=label)

        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNES), method="POST", json=expected_response)

        base_model = Model(self.model, params=None, credentials=credentials)
        tuned_model = base_model.tune(
            name=label,
            method="mpt",
            task="generation",
            training_file_ids=["id1"],
            hyperparameters=hyperparams,
        )
        assert tuned_model.model == expected_response["results"]["id"]

    def test_status(self, credentials, httpx_mock: HTTPXMock):
        label = "test_label"
        model_id = self.model
        tune_id = SimpleResponse.get_tune(model_id=model_id, name=label)["results"]["id"]

        tuned_model = Model(tune_id, params=None, credentials=credentials)

        expected_response = SimpleResponse.get_tune()
        httpx_mock.add_response(
            url=match_endpoint(TunesRouter.TUNES, tuned_model.model), method="GET", json=expected_response
        )

        assert tuned_model.status() == expected_response["results"]["status"]

    def test_info(self, credentials, httpx_mock: HTTPXMock):
        model_id = "google/flan-t5-xl"
        response = SimpleResponse.models()
        card = [m for m in response["results"] if m["id"] == model_id]
        info = ModelCard(**card[0])

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.MODELS), method="GET", json=response)

        model = Model(model_id, params=None, credentials=credentials)
        assert info == model.info()

    def test_models(self, httpx_mock: HTTPXMock):
        response = SimpleResponse.models()

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.MODELS), method="GET", json=response)

        assert Model.models(service=self.service) == ModelList(**response).results

    def test_available(self, credentials, httpx_mock: HTTPXMock):
        response = SimpleResponse.models()

        httpx_mock.add_response(url=match_endpoint(ServiceInterface.MODELS), method="GET", json=response)

        model_id = "google/flan-t5-xl"
        model = Model(model_id, params=None, credentials=credentials)
        assert model.available() is True

        model_id = "random"
        model = Model(model_id, params=None, credentials=credentials)
        assert model.available() is False

    @pytest.mark.parametrize("generate_params", [([],), (1,), ("",), (CreateTuneHyperParams())])
    def test_invalid_generate_parameters(self, generate_params, credentials):
        with pytest.raises(ValueError):
            model = Model("google/flan-ul2", params=generate_params, credentials=credentials)
            model.generate(prompts=[])
