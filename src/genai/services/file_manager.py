import logging
import os
from collections import OrderedDict
from typing import Union

from genai.credentials import Credentials
from genai.exceptions.genai_exception import GenAiException
from genai.schemas import FileListParams
from genai.schemas.responses import FileInfoResult, FilesListResponse
from genai.services import ServiceInterface
from genai.utils.service_utils import _get_service

logger = logging.getLogger(__name__)


class FileManager:
    """Class for managing files on the server."""

    @staticmethod
    def list_files(
        credentials: Credentials = None,
        service: ServiceInterface = None,
        params: FileListParams = None,
    ) -> FilesListResponse:
        """List all files on the server.

        Args:
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.
            params (FileListParams, optional): Parameters for listing files.

        Returns:
            FilesListResponse: Response from the server.
        """
        service = _get_service(credentials, service)

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
    def file_metadata(
        file_id: str, credentials: Credentials = None, service: ServiceInterface = None
    ) -> FileInfoResult:
        """Get metadata from a file.

        Args:
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.
            file_id (str): File id.

        Returns:
            FileInfoResult: Response from the server.
        """
        service = _get_service(credentials, service)

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
    def read_file(
        file_id: str, credentials: Credentials = None, service: ServiceInterface = None
    ) -> Union[list[dict], dict]:
        """Read a file from the server and return the file content.

        Args:
            file_id (str): File id or list of file ids.
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.

        Returns:
            Union[list[dict], dict]: File content.
        """
        service = _get_service(credentials, service)

        try:
            response = service._files.read_file(file_id=file_id)

            if response.status_code == 200:
                return response.content.decode("utf-8")
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def upload_file(
        file_path: str,
        purpose: str,
        credentials: Credentials = None,
        service: ServiceInterface = None,
    ) -> FileInfoResult:
        """Upload a file to the server.

        Args:
            file_path (str): Path to the file to be uploaded. The file needs to be in JSON or JSON Lines format.
                Format of the data depends on the task_id.
            purpose (str): Purpose of the file to be uploaded. Currently accepts only "tune" or "template".
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.

        Raises:
            GenAiException: If file does not exist or has incorrect format or if incorrect purpose.

        Returns:
            FileInfoResult: Response from the server.
        """

        if purpose != "tune" and purpose != "template":
            raise GenAiException(ValueError("Purpose must be 'tune' or 'template'"))

        # check if file exists
        if not os.path.isfile(file_path):
            raise GenAiException(ValueError(f"File {file_path} does not exist"))

        # check if file is json or jsonl
        if not file_path.endswith(".json") and not file_path.endswith(".jsonl"):
            raise GenAiException(ValueError(f"File {file_path} must be in json or jsonl format"))

        multipart_form_data = {
            "purpose": (None, purpose),
            "file": (file_path, open(file_path, "rb")),
        }

        multipart_form_data = FileManager._validate_mmultipart_form_data_order(multipart_form_data)

        service = _get_service(credentials, service)

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
    def delete_file(file_id: str, credentials: Credentials = None, service: ServiceInterface = None) -> dict:
        """Delete a file from the server.

        Args:
            file_id (str): File id.
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.

        Returns:
            dict: Response from the server.
        """
        service = _get_service(credentials, service)

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
