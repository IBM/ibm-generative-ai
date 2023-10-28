import os
import pathlib
from unittest.mock import mock_open, patch

import pytest
from pytest_httpx import HTTPXMock

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
from genai.utils.request_utils import match_endpoint
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestTunes:
    def setup_method(self):
        self.service_router = TunesRouter(service_url="http://service_url", api_key="API_KEY")
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
    def test_list_tunes(self, credentials, list_params, httpx_mock: HTTPXMock):
        list_response = SimpleResponse.tunes(params=list_params)
        expected_response = TunesListResponse(**list_response)

        httpx_mock.add_response(
            url=match_endpoint(TunesRouter.TUNES, query_params=list_params), method="GET", json=list_response
        )

        f = TuneManager.list_tunes(credentials=credentials, params=list_params)
        assert f == expected_response

    def test_tune_list_api_call(self, list_params, httpx_mock: HTTPXMock):
        list_response = SimpleResponse.tunes(params=list_params)
        httpx_mock.add_response(
            url=match_endpoint(TunesRouter.TUNES, query_params=list_params),
            method="GET",
            json=SimpleResponse.tunes(params=list_params),
        )

        g = self.service_router.list_tunes(params=list_params)
        assert g.json() == list_response

    def test_list_tunes_wrong_params(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.list_tunes(params="params")
            assert e.message == "params must be of type TunesListParams."

    def test_list_tunes_wrong_params_type(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.list_tunes(params=123)
            assert e.message == "params must be of type TunesListParams."

    # Test delete tunes function
    def test_delete_tune(self, credentials, httpx_mock: HTTPXMock):
        expected_response = {"status": "success"}
        httpx_mock.add_response(
            url=match_endpoint(TunesRouter.TUNES, "tune_id"), method="DELETE", json=expected_response
        )

        with pytest.raises(Exception) as e:
            file_response = TuneManager.delete_tune(credentials=credentials, tune_id="tune_id")
            assert e.message == "Tune can not be deleted until is completed or failed."
            assert file_response == expected_response

    def test_delete_tune_api_call(self, httpx_mock: HTTPXMock):
        expected = {"status": "success"}
        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNES, "tune_id"), method="DELETE", json=expected)

        tune_response = self.service_router.delete_tune(tune_id="tune_id")

        assert tune_response.json() == {"status": "success"}

    def test_tune_delete_wrong_params(self):
        with pytest.raises(Exception) as e:
            self.service_router.delete_tune(tune_id=123)
            assert e.message == "Tune not found, tune_id must be of type str"

    # Test get tune function

    def test_get_tune(self, credentials, httpx_mock: HTTPXMock):
        get_tune_response = SimpleResponse.tunes(tune_id="tune_id")
        expected_response = TuneInfoResult(**get_tune_response["results"])

        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNES, "tune_id"), method="GET", json=get_tune_response)

        tune_response = TuneManager.get_tune(credentials=credentials, tune_id="tune_id")
        assert tune_response == expected_response

    def test_get_tune_api_call(self, httpx_mock: HTTPXMock):
        expected = SimpleResponse.tunes()
        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNES, "tune_id"), method="GET", json=expected)
        g = self.service_router.get_tune(tune_id="tune_id")
        assert g.json() == expected

    def test_get_tune_wrong_params(self):
        with pytest.raises(Exception) as e:
            self.service_router.get_tune(tune_id=123)
            assert e.message == "Tune not found, tune_id must be of type str"

    # Test create tune function

    def test_create_tune(self, create_params, credentials, httpx_mock: HTTPXMock):
        create_response = SimpleResponse.tunes(params=create_params)
        expected_create_response = TuneInfoResult(**create_response["results"])

        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNES), method="POST", json=create_response)

        tune_response = TuneManager.create_tune(credentials=credentials, params=create_params)

        assert tune_response == expected_create_response

    def test_create_tune_api_call(self, create_params, httpx_mock: HTTPXMock):
        expected = SimpleResponse.tunes()
        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNES), method="POST", json=expected)

        g = self.service_router.create_tune(params=create_params)
        assert g.json() == expected

    def test_create_tune_wrong_params(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.create_tune(params="params")
            assert e.message == "params must be of type dict as CreateTuneParams."

    def test_create_tune_wrong_params_type(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.create_tune(params=123)
            assert e.message == "params must be of type dict as CreateTuneParams."

    # Test get tune methods function

    def test_get_tune_methods(self, credentials, httpx_mock: HTTPXMock):
        tune_methods_response = SimpleResponse.get_tune_methods()
        expected_response = TuneMethodsGetResponse(**tune_methods_response)

        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNE_METHODS), method="GET", json=tune_methods_response)

        tune_response = TuneManager.get_tune_methods(credentials=credentials)
        assert tune_response.results == expected_response.results

    def test_get_tune_methods_api_call(self, httpx_mock: HTTPXMock):
        expected = SimpleResponse.get_tune_methods()

        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNE_METHODS), method="GET", json=expected)

        g = self.service_router.get_tune_methods()
        assert g.json() == expected

    # Test download tune assets function
    @patch("builtins.open", new=mock_open(read_data="some data"), create=True)
    def test_download_assets(self, credentials, download_assets_params, tmp_path, httpx_mock: HTTPXMock):
        output_path = pathlib.Path(self.asset_path, tmp_path, "tune_assets").resolve()

        httpx_mock.add_response(
            url=match_endpoint(TunesRouter.TUNES, "/some-tune-id"),
            method="GET",
            status_code=500,
        )
        httpx_mock.add_response(url=match_endpoint(TunesRouter.TUNES, "tune_id/content/encoder"), method="GET")

        with pytest.raises(Exception) as e:
            TuneManager.download_tune_assets(
                credentials=credentials, params=download_assets_params, output_path=output_path
            )
            assert e.message == "Tune can not be deleted until is completed or failed."
            assert os.path.exists(output_path)
            assert os.path.isdir(output_path)
