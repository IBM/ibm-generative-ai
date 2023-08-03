import os
import pathlib
from unittest.mock import MagicMock, mock_open, patch

import pytest

from genai import Credentials
from genai.exceptions import GenAiException
from genai.routers.tunes import TunesRouter
from genai.schemas.responses import (
    TuneInfoResult,
    TuneMethodsGetResponse,
    TunesListResponse,
)
from genai.schemas.tunes_params import (
    CreateTuneParams,
    DownloadAssetsParams,
    TunesListParams,
)
from genai.services.tune_manager import TuneManager
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestTunes:
    def setup_method(self):
        self.service_router = TunesRouter(service_url="SERVICE_URL", api_key="API_KEY")
        self.path = pathlib.Path(__file__).parent.resolve()
        self.asset_path = pathlib.Path(__file__, "..", "assets").resolve()

    @pytest.fixture
    def list_params(self):
        return TunesListParams(limit=10, offset=0)

    @pytest.fixture
    def download_assets_params(self):
        return DownloadAssetsParams(id="some-tune-id", content="encoder")

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
        return Credentials("GENAI_KEY")

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

        with pytest.raises(Exception) as e:
            file_response = TuneManager.delete_tune(credentials=credentials, tune_id="tune_id")
            assert e.message == "Tune can not be deleted until is completed or failed."
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

    # Test get tune methods function

    @patch("genai.services.RequestHandler.get")
    def test_get_tune_methods(self, mock_requests, credentials):
        tune_methods_response = SimpleResponse.get_tune_methods()
        expected_response = TuneMethodsGetResponse(**tune_methods_response)

        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = tune_methods_response
        mock_requests.return_value = mock_response

        tune_response = TuneManager.get_tune_methods(credentials=credentials)
        assert tune_response.results == expected_response.results

    @patch("genai.services.RequestHandler.get")
    def test_get_tune_methods_api_call(self, mock_requests):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = SimpleResponse.get_tune_methods()
        mock_requests.return_value = mock_response
        g = self.service_router.get_tune_methods()
        assert g == mock_response

    # Test download tune assets function

    @patch("genai.services.RequestHandler.get")
    @patch("builtins.open", new=mock_open(read_data="some data"), create=True)
    def test_download_assets(self, mock_request, credentials, download_assets_params, tmp_path):
        output_path = pathlib.Path(self.asset_path, tmp_path, "tune_assets").resolve()
        mock_request.json.return_value = MagicMock(status_code=200)

        with pytest.raises(Exception) as e:
            TuneManager.download_tune_assets(
                credentials=credentials, params=download_assets_params, output_path=output_path
            )
            assert e.message == "Tune can not be deleted until is completed or failed."
            assert os.path.exists(output_path)
            assert os.path.isdir(output_path)
