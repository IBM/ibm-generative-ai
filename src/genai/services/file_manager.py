import logging
import os
from collections import OrderedDict
from typing import Union

from genai.credentials import Credentials
from genai.exceptions.genai_exception import GenAiException

from genai.services.service_interface import ServiceInterface
from genai.schemas.files_params import FileListParams
from genai.schemas.responses import FileInfoResult, FilesListResponse


logger = logging.getLogger(__name__)


class FileManager:
    """Class for managing files on the server."""

    @staticmethod
    def list_files(credentials: Credentials, params: FileListParams) -> FilesListResponse:
        """List all files on the server.

        Args:
            params (FileListParams): Parameters for listing files.

        Returns:
            FilesListResponse: Response from the server.
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
        try:
            response = service._files.list_files(params=params)

            if response.status_code == 200:
                response = response.json()
                responses = FilesListResponse(**response)
                return responses
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def file_metadata(credentials: Credentials, file_id: str) -> FileInfoResult:
        """Get metadata from a file.

        Args:
            file_id (str): File id.

        Returns:
            FileInfoResult: Response from the server.
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
        try:
            response = service._files.get_file_metadata(file_id=file_id)

            if response.status_code == 200:
                response = response.json()
                return FileInfoResult(**response["results"])
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def read_files(credentials: Credentials, file_id: Union[list[str], str]) -> Union[list[dict], dict]:
        """Read a file from the server and return the file content.

        Args:
            file_id (Union[list[str], str]): File id or list of file ids.

        Returns:
            Union[list[dict], dict]: File content.
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
        try:
            response = service._files.read_file(file_id=file_id)

            if response.status_code == 200:
                return response.content.decode("utf-8")
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def upload_file(credentials: Credentials, file_path: str, purpose: str) -> FileInfoResult:
        """Upload a file to the server.

        Args:
            file_path (str): Path to the file to be uploaded. The file needs to be in JSON or JSON Lines format.
                Format of the data depends on the task_id.
            purpose (str): Purpose of the file to be uploaded. Currently accepts only "tune" or "template"

        Raises:
            GenAiException: If file does not exist.
            GenAiException: If file is not in json or jsonl format.
            GenAiException: If purpose is not 'tune' or 'template'.

        Returns:
            FileInfoResult: Response from the server.
        """

        if purpose != "tune" and purpose != "template":
            raise GenAiException("Purpose must be 'tune' or 'template'")

        # check if file exists
        if not os.path.isfile(file_path):
            raise GenAiException(f"File {file_path} does not exist")

        # check if file is json or jsonl
        if not file_path.endswith(".json") and not file_path.endswith(".jsonl"):
            raise GenAiException(f"File {file_path} must be in json or jsonl format")

        multipart_form_data = {
            "purpose": (None, purpose),
            "file": (file_path, open(file_path, "rb")),
        }

        multipart_form_data = FileManager._validate_mmultipart_form_data_order(multipart_form_data)

        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
        try:
            response = service._files.upload_file(multipart_form_data=multipart_form_data)

            if response.status_code == 201:
                response = response.json()
                return FileInfoResult(**response["results"])
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def delete_file(credentials: Credentials, file_id: str) -> dict:
        """Delete a file from the server.

        Args:
            file_id (str): File id.

        Returns:
            dict: Response from the server.
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
        try:
            response = service._files.delete_file(file_id=file_id)
            if response.status_code == 204:
                return {"status": "success"}
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def _validate_mmultipart_form_data_order(form_data: dict):
        "To upload a file, the required body needs to be in a specific order."
        "purpose needs to be placed before file in the multipart/form-data payload."
        desired_order = ["purpose", "file"]

        if list(form_data.keys()) != desired_order:
            # Reorder the dictionary using an OrderedDict
            form_data = OrderedDict((key, form_data.get(key)) for key in desired_order if key in form_data)
        return form_data
