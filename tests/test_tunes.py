from unittest.mock import MagicMock, patch

import pytest

from genai import Credentials
from genai.exceptions import GenAiException
from genai.routers.tunes import TunesRouter
from genai.schemas.responses import TuneInfoResult, TunesListResponse
from genai.schemas.tunes_params import CreateTuneParams, TunesListParams
from genai.services.tune_manager import TuneManager
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestTunes:
    def setup_method(self):
        self.service_router = TunesRouter(service_url="SERVICE_URL", api_key="API_KEY")

    @pytest.fixture
    def list_params(self):
        return TunesListParams(limit=10, offset=0)

    @pytest.fixture
    def create_params(self):
        return CreateTuneParams(
            name="Test",
            model_id="some-model-id",
            method_id="some-method-id",
            task_id="generation",
            training_file_ids=["some-file-id"],
        )

    @pytest.fixture
    def credentials(self):
        return Credentials("GENAI_APY_KEY")

    # Test list tunes function
    @patch("genai.services.RequestHandler.get")
    def test_list_tunes(self, mock_requests, credentials, list_params):
        list_response = SimpleResponse.tunes(params=list_params)
        expected_response = TunesListResponse(**list_response)

        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = list_response
        mock_requests.return_value = mock_response

        f = TuneManager.list_tunes(credentials=credentials, params=list_params)
        assert f == expected_response

    @patch("genai.services.RequestHandler.get")
    def test_tune_list_api_call(self, mock_requests, list_params):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.tunes()
        mock_requests.return_value = mock_response

        g = self.service_router.list_tunes(params=list_params)
        assert g == mock_response

    def test_list_tunes_wrong_params(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.list_tunes(params="params")
            assert e.message == "params must be of type TunesListParams."

    def test_list_tunes_wrong_params_type(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.list_tunes(params=123)
            assert e.message == "params must be of type TunesListParams."

    # Test delete tunes function
    @patch("genai.services.RequestHandler.delete")
    def test_delete_tune(self, mocker, credentials):
        expected_response = {"status": "success"}
        response = MagicMock(status_code=204)
        response.json.return_value = expected_response
        mocker.return_value = response

        file_response = TuneManager.delete_tune(credentials=credentials, tune_id="tune_id")

        assert file_response == expected_response

    @patch("genai.services.RequestHandler.delete")
    def test_delete_tune_api_call(self, mocker):
        response = MagicMock(status_code=204)
        response.json.return_value = {"status": "success"}
        mocker.return_value = response

        tune_response = self.service_router.delete_tune(tune_id="tune_id")

        assert tune_response == response

    def test_tune_delete_wrong_params(self):
        with pytest.raises(Exception) as e:
            self.service_router.delete_tune(tune_id=123)
            assert e.message == "Tune not found, tune_id must be of type str"

    # Test get tune function

    @patch("genai.services.RequestHandler.get")
    def test_get_tune(self, mock_requests, credentials):
        get_tune_response = SimpleResponse.tunes(tune_id="tune_id")
        expected_response = TuneInfoResult(**get_tune_response["results"])

        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = get_tune_response
        mock_requests.return_value = mock_response

        tune_response = TuneManager.get_tune(credentials=credentials, tune_id="tune_id")
        assert tune_response == expected_response

    @patch("genai.services.RequestHandler.get")
    def test_get_tune_api_call(self, mock_requests):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.tunes()
        mock_requests.return_value = mock_response
        g = self.service_router.get_tune(tune_id="tune_id")
        assert g == mock_response

    def test_get_tune_wrong_params(self):
        with pytest.raises(Exception) as e:
            self.service_router.get_tune(tune_id=123)
            assert e.message == "Tune not found, tune_id must be of type str"

    # Test create tune function

    @patch("genai.services.RequestHandler.post")
    def test_create_tune(self, mocker, create_params, credentials):
        create_response = SimpleResponse.tunes(params=create_params)
        expected_create_response = TuneInfoResult(**create_response["results"])

        response = MagicMock(status_code=200)
        response.json.return_value = create_response
        mocker.return_value = response

        tune_response = TuneManager.create_tune(credentials=credentials, params=create_params)

        assert tune_response == expected_create_response

    @patch("genai.services.RequestHandler.post")
    def test_create_tune_api_call(self, mock_requests, create_params):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.tunes()
        mock_requests.return_value = mock_response

        g = self.service_router.create_tune(params=create_params)
        assert g == mock_response

    def test_create_tune_wrong_params(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.create_tune(params="params")
            assert e.message == "params must be of type dict as CreateTuneParams."

    def test_create_tune_wrong_params_type(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.create_tune(params=123)
            assert e.message == "params must be of type dict as CreateTuneParams."
