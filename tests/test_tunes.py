from unittest.mock import MagicMock, patch

import pytest

from genai import Credentials
from genai.exceptions import GenAiException
from genai.routers.tunes import TunesRouter
from genai.schemas.tunes_params import CreateTuneParams, TunesListParams
from genai.services.tune_manager import TuneManager
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestTunes:
    def setup_method(self):
        self.service_router = TunesRouter(service_url="SERVICE_URL", api_key="API_KEY")

    @pytest.fixture
    def params(self):
        return TunesListParams(limit=10, offset=0)

    @pytest.fixture
    def credentials(self):
        return Credentials("GENAI_KEY")

    # Test list tunes function
    @patch("genai.services.RequestHandler.get")
    def test_tune_list_api_call(self, mock_requests, params):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.tunes()
        mock_requests.return_value = mock_response

        g = self.service_router.list_tunes(params=params)
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
    def test_tune_delete_wrong_params(self):
        with pytest.raises(Exception) as e:
            self.service_router.delete_tune(tune_id=123)
            assert e.message == "Tune not found, tune_id must be of type str"

    @patch("genai.services.RequestHandler.delete")
    def test_delete_tune(self, mocker):
        response = MagicMock(status_code=204)
        response.json.return_value = {"status": "success"}
        mocker.return_value = response

        tune_response = self.service_router.delete_tune(tune_id="tune_id")

        assert tune_response == response

    # Test get tune function

    @patch("genai.services.RequestHandler.get")
    def test_get_tune(self, mock_requests):
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
    def test_create_tune(self, mock_requests, params: CreateTuneParams):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.tunes()
        mock_requests.return_value = mock_response

        g = self.service_router.create_tune(params=params)
        assert g == mock_response

    def test_create_tune_wrong_params(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.create_tune(params="params")
            assert e.message == "params must be of type dict as CreateTuneParams."

    def test_create_tune_wrong_params_type(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.create_tune(params=123)
            assert e.message == "params must be of type dict as CreateTuneParams."

    # Test download tune assets function

    @patch("genai.services.RequestHandler.get")
    def test_get_tune_methods(self, credentials):
        expected_response = MagicMock(status_code=200)

        tune_manager = TuneManager()
        tune_response = tune_manager.get_tune_methods(credentials=credentials)

        print("\n\nTUNE RESPONSE: ", tune_response)
        print("\n\nEXPECTED REPONSE: ", expected_response)

        assert tune_response == expected_response
