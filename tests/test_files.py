import os
import pathlib

import pytest
from pydantic import ValidationError
from pytest_httpx import HTTPXMock

from genai import Credentials
from genai.exceptions import GenAiException
from genai.routers import FilesRouter
from genai.schemas import FileListParams
from genai.schemas.responses import FileInfoResult, FilesListResponse
from genai.services.file_manager import FileManager
from tests.assets.response_helper import SimpleResponse
from tests.utils import match_endpoint


@pytest.mark.unit
class TestFiles:
    def setup_method(self):
        # mock object for the API call
        self.service_router = FilesRouter(service_url="http://service_url", api_key="API_KEY")
        self.path = pathlib.Path(__file__).parent.resolve()
        self.asset_path = str(self.path) + os.sep + "assets" + os.sep

    @pytest.fixture
    def params(self):
        return FileListParams(limit=10, offset=0)

    @pytest.fixture
    def credentials(self):
        return Credentials("GENAI_APY_KEY")

    @pytest.fixture
    def file_to_upload(self):
        return self.asset_path + "file_to_tune.json"

    @pytest.fixture
    def not_valid_file_to_upload(self):
        return self.asset_path + "file_to_tune.csv"

    @pytest.fixture
    def multipart_form_data(self, file_to_upload):
        return {
            "purpose": (None, "test"),
            "task_id": (None, "test"),
            "file": (file_to_upload, open(file_to_upload, "rb")),
        }

    @pytest.fixture
    def task_id_types(self):
        return ["generation", "classification", "summarization"]

    # test list files function
    def test_list_files(self, params, credentials, httpx_mock: HTTPXMock):
        response = SimpleResponse.files(params=params)
        expected_response = FilesListResponse(**response)
        httpx_mock.add_response(url=match_endpoint(self.service_router.FILES), method="GET", json=response)

        f = FileManager.list_files(credentials=credentials)
        assert f == expected_response

    def test_file_list_api_call(self, params, httpx_mock: HTTPXMock):
        response = SimpleResponse.files()
        httpx_mock.add_response(
            url=match_endpoint(self.service_router.FILES, query_params=params), method="GET", json=response
        )
        f = self.service_router.list_files(params=params)
        assert f.json() == response

    def test_file_list_api_call_with_wrong_params(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.list_files(params="params")
            assert e.message == "params must be of type FileListParams."

    def test_file_list_api_call_with_wrong_params_type(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.list_files(params=123)
            assert e.message == "params must be of type FileListParams."

    # test file metadata function
    def test_file_metadata_api_call(self, httpx_mock: HTTPXMock):
        file_id = "file_id"
        response = SimpleResponse.files(file_id=file_id)
        httpx_mock.add_response(url=match_endpoint(self.service_router.FILES, file_id), method="GET", json=response)

        f = self.service_router.get_file_metadata(file_id=file_id)
        assert f.json() == response

    def test_file_metadata_api_call_wrong_id(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.get_file_metadata(file_id=123)
            assert e.message == "File not found, file_id must be of type str"

    def test_file_metadata(self, credentials, httpx_mock: HTTPXMock):
        file_metadata_response = SimpleResponse.files(file_id="file_id")
        expected_response = FileInfoResult(**file_metadata_response["results"])

        httpx_mock.add_response(
            url=match_endpoint(self.service_router.FILES, "file_id"), method="GET", json=file_metadata_response
        )

        file_response = FileManager.file_metadata(credentials=credentials, file_id="file_id")

        assert file_response == expected_response

    # test file read function
    def test_read_file_api_call(self, httpx_mock: HTTPXMock):
        response = SimpleResponse.files(file_id="file_id")
        httpx_mock.add_response(
            url=match_endpoint(self.service_router.FILES, "file_id", "content"), method="GET", json=response
        )
        f = self.service_router.read_file(file_id="file_id")
        assert f.json() == response

    def test_read_file_api_call_wrong_id(self):
        with pytest.raises(Exception) as e:
            self.service_router.read_file(file_id=123)
            assert e.message == "File not found, file_id must be of type str"

    def test_read_file(self, credentials, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=match_endpoint(self.service_router.FILES, "file_id", "content"), method="GET", content="file_content"
        )

        file_response = FileManager.read_file(credentials=credentials, file_id="file_id")

        assert file_response == "file_content"

    # test file delete function

    def test_delete_file_api_call(self, httpx_mock: HTTPXMock):
        response = {"status": "success"}
        httpx_mock.add_response(
            url=match_endpoint(self.service_router.FILES, "file_id"), method="DELETE", json=response
        )

        f = self.service_router.delete_file(file_id="file_id")
        assert f.json() == response

    def test_file_delete_api_call_wrong_id(self):
        with pytest.raises(Exception) as e:
            self.service_router.delete_file(file_id=123)
            assert e.message == "File not found, file_id must be of type str"

    def test_delete_file(self, credentials, httpx_mock: HTTPXMock):
        response = {"status": "success"}
        httpx_mock.add_response(
            url=match_endpoint(self.service_router.FILES, "file_id"), method="DELETE", json=response
        )

        file_response = FileManager.delete_file(credentials=credentials, file_id="file_id")

        assert file_response == response

    # test file upload function
    def test_upload_file_api_call(self, multipart_form_data, httpx_mock: HTTPXMock):
        response = SimpleResponse.files(multipart_form_data=multipart_form_data)

        httpx_mock.add_response(url=match_endpoint(self.service_router.FILES), method="POST", json=response)

        f = self.service_router.upload_file(multipart_form_data=multipart_form_data)
        assert f.json() == response

    def test_file_uplod_api_call_wrong_forms(self):
        with pytest.raises(GenAiException) as e:
            self.service_router.upload_file(multipart_form_data="form_data")
            assert e.message == "multipart_form_data must be of type dict"
        with pytest.raises(GenAiException) as e:
            self.service_router.upload_file(multipart_form_data="")
            assert e.message == "multipart_form_data must be of type dict"

    def test_file_upload(self, multipart_form_data, credentials, file_to_upload, httpx_mock: HTTPXMock):
        upload_response = SimpleResponse.files(multipart_form_data=multipart_form_data)
        expected_upload_response = FileInfoResult(**upload_response["results"])

        httpx_mock.add_response(url=match_endpoint(self.service_router.FILES), method="POST", json=upload_response)

        file_response = FileManager.upload_file(credentials=credentials, file_path=file_to_upload, purpose="tune")

        assert file_response == expected_upload_response

    def test_file_upload_with_wrong_params_type(self, credentials, file_to_upload):
        with pytest.raises(GenAiException) as e:
            FileManager.upload_file(credentials=credentials, file_path=file_to_upload, purpose=123)
            assert e.message == "purpose is not valid, must be one of tune or template"

    def test_file_upload_with_wrong_file_path(self, credentials):
        with pytest.raises(GenAiException) as e:
            FileManager.upload_file(credentials=credentials, file_path="file_path", purpose="tune")
            assert e.message == "File not found, file_path does not exist"

    def test_file_upload_is_json(self, credentials, not_valid_file_to_upload):
        with pytest.raises(GenAiException) as e:
            FileManager.upload_file(credentials=credentials, file_path=not_valid_file_to_upload, purpose="tune")
            assert e.message == "File must be in json or jsonl format"

    def test_file_list_params_schema(self):
        with pytest.raises(ValidationError) as e:
            FileListParams(limit="200", offset=0)
            assert e.message == "Ensure the limit value is less than or equal to 100"
        with pytest.raises(ValidationError) as e:
            FileListParams(limit=[100], offset="0")
            assert e.message == "Ensure limite value is a valid integer and not list"
        with pytest.raises(ValidationError) as e:
            FileListParams(limit=100, offset=[0])
            assert e.message == "Ensure offset value is a valid integer and not list"
        with pytest.raises(ValidationError) as e:
            FileListParams(limit=100, offset=0, search=["test"])
            assert e.message == "Ensure search value is a valid string"
