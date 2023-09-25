from genai.exceptions import GenAiException
from genai.schemas.files_params import FileListParams, MultipartFormData
from genai.services.request_handler import RequestHandler
from genai.utils.request_utils import sanitize_params


class FilesRouter:
    FILES = "/v1/files"

    def __init__(self, service_url: str, api_key: str) -> None:
        self.service_url = service_url.rstrip("/")
        self.key = api_key

    def list_files(self, params: FileListParams = None):
        """List all files on the server.

        Args:
            params (FileListParams, optional): Parameters for listing files.

        Returns:
            Any: json from querying for file list.
        """
        try:
            params = sanitize_params(params)
            endpoint = self.service_url + FilesRouter.FILES
            return RequestHandler.get(endpoint, key=self.key, parameters=params)
        except Exception as e:
            raise GenAiException(e)

    def get_file_metadata(self, file_id: str):
        """Get the file metadata from the server.

        Args:
            file_id (str): Id of the file to be retrieved.

        Returns:
            Any: json from querying for file retrieval.
        """
        try:
            endpoint = self.service_url + FilesRouter.FILES + "/" + file_id
            return RequestHandler.get(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def read_file(self, file_id: str):
        """Read the content of a file from the server.

        Args:
            file_id (str): Id of the file to be retrieved.

        Returns:
            Any: file contents.
        """
        try:
            endpoint = self.service_url + FilesRouter.FILES + "/" + file_id + "/content"
            return RequestHandler.get(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def delete_file(self, file_id: str):
        """Delete a file from the server.

        Args:
            file_id (str): Id of the file to be deleted.

        Returns:
            Any: json from querying for file deletion.
        """
        try:
            endpoint = self.service_url + FilesRouter.FILES + "/" + file_id
            return RequestHandler.delete(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def upload_file(self, multipart_form_data: MultipartFormData):
        """Upload a file to the server.

        Args:
            multipart_form_data (MultipartFormData): Form with the required params to be uploaded.

        Returns:
            Any: json from file uploaded.
        """
        try:
            endpoint = self.service_url + FilesRouter.FILES
            return RequestHandler.post(endpoint, key=self.key, files=multipart_form_data)
        except Exception as e:
            raise GenAiException(e)
