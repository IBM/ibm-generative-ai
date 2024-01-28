from pathlib import Path
from typing import Optional, Union

from genai._types import EnumLike
from genai._utils.general import to_enum, to_enum_optional
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
    get_service_action_metadata,
    set_service_action_metadata,
)
from genai._utils.validators import assert_is_not_empty_string
from genai.schema import (
    FileCreateResponse,
    FileIdRetrieveResponse,
    FileListSortBy,
    FilePurpose,
    FileRetrieveResponse,
    SortDirection,
)
from genai.schema._api import (
    _FileCreateParametersQuery,
    _FileCreateRequest,
    _FileIdContentRetrieveParametersQuery,
    _FileIdDeleteParametersQuery,
    _FileIdRetrieveParametersQuery,
    _FileRetrieveParametersQuery,
)
from genai.schema._endpoints import (
    FileCreateEndpoint,
    FileIdContentRetrieveEndpoint,
    FileIdDeleteEndpoint,
    FileIdRetrieveEndpoint,
    FileRetrieveEndpoint,
)

__all__ = ["FileService"]


class FileService(BaseService[BaseServiceConfig, BaseServiceServices]):
    @set_service_action_metadata(endpoint=FileCreateEndpoint)
    def create(
        self,
        file_path: Union[str, Path],
        purpose: EnumLike[FilePurpose],
    ) -> FileCreateResponse:
        """
        Args:
            file_path: The path to the local file that will be uploaded.
            purpose: The purpose of the file to be created.

        Raises:
            ValueError: If the file does not exist or if the file format is not supported.
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        file_path = Path(file_path)
        if not file_path.is_file():
            raise ValueError(f"File {file_path} does not exist!")

        if not file_path.name.endswith(".json") and not file_path.name.endswith(".jsonl"):
            raise ValueError(f"File {file_path} must be in 'json' or jsonl 'format'!")

        with file_path.open("rb") as file_read_stream:
            request_body = _FileCreateRequest(purpose=to_enum(FilePurpose, purpose), file=b"").model_dump(
                exclude="file"
            )
            self._log_method_execution("File Create", **request_body)

            with self._get_http_client() as client:
                metadata = get_service_action_metadata(self.create)
                response = client.post(
                    url=self._get_endpoint(metadata.endpoint),
                    params=_FileCreateParametersQuery().model_dump(),
                    files={"file": (file_path.name, file_read_stream)},
                    data=request_body,
                )
                return FileCreateResponse(**response.json())

    @set_service_action_metadata(endpoint=FileIdContentRetrieveEndpoint)
    def read(
        self,
        id: str,
    ) -> str:
        """
        Args:
            id (str): The ID of the file to be read.

        Returns:
            str: The content of the file as a UTF-8 decoded string.

        Raises:
            ValueError: If the provided `id` is an empty string.
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.

        """
        assert_is_not_empty_string(id)
        self._log_method_execution("File Read", id=id)
        metadata = get_service_action_metadata(self.read)

        with self._get_http_client() as client:
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_FileIdContentRetrieveParametersQuery().model_dump(),
            )
            return response.content.decode("utf-8")

    @set_service_action_metadata(endpoint=FileIdRetrieveEndpoint)
    def retrieve(
        self,
        id: str,
    ) -> FileIdRetrieveResponse:
        """
        Args:
            id (str): The ID of the file to retrieve.

        Returns:
            FileIdRetrieveResponse: The response object containing the retrieved file information.

        Raises:
            ValueError: If the ID is an empty string.
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.

        """
        assert_is_not_empty_string(id)
        self._log_method_execution("File Retrieve", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.retrieve)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_FileIdRetrieveParametersQuery().model_dump(),
            )
            return FileIdRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=FileRetrieveEndpoint)
    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[EnumLike[FileListSortBy]] = None,
        direction: Optional[EnumLike[SortDirection]] = None,
        search: Optional[str] = None,
        purpose: Optional[EnumLike[FilePurpose]] = None,
        format_id: Optional[int] = None,
    ) -> FileRetrieveResponse:
        """
        Args:
            limit: The maximum number of files to retrieve. Defaults to None.
            offset: The number of files to skip before starting retrieval. Defaults to None.
            sort_by: The field to sort the files by.
            direction: The sort direction. Can be either "asc" or "desc". Defaults to None.
            search: The search string to filter files by. Defaults to None.
            purpose: The purpose of the files. Can be one of the values from the FilePurpose enum. Defaults to None.
            format_id: The ID of the file format. Defaults to None.

        Raises:
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
            ValidationError: In case of provided parameters are invalid.
        """
        request_params = _FileRetrieveParametersQuery(
            limit=limit,
            offset=offset,
            sort_by=to_enum_optional(sort_by, FileListSortBy),
            direction=to_enum_optional(direction, SortDirection),
            search=search,
            purpose=to_enum_optional(purpose, FilePurpose),
            format_id=format_id,
        ).model_dump()
        self._log_method_execution("File List", **request_params)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.list)
            response = client.get(
                url=self._get_endpoint(metadata.endpoint),
                params=request_params,
            )
            return FileRetrieveResponse(**response.json())

    @set_service_action_metadata(endpoint=FileIdDeleteEndpoint)
    def delete(self, id: str) -> None:
        """
        Deletes a file with the given ID.

        Args:
            id: The ID of the file to be deleted.

        Raises:
            ValueError: If the ID is an empty string.
            ApiResponseException: In case of a known API error.
            ApiNetworkException: In case of unhandled network error.
        """
        assert_is_not_empty_string(id)
        self._log_method_execution("File Delete", id=id)

        with self._get_http_client() as client:
            metadata = get_service_action_metadata(self.delete)
            client.delete(
                url=self._get_endpoint(metadata.endpoint, id=id),
                params=_FileIdDeleteParametersQuery().model_dump(),
            )
