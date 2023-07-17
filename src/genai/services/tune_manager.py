import logging
import os
import pathlib

from genai.credentials import Credentials
from genai.exceptions.genai_exception import GenAiException
from genai.schemas.responses import (
    TuneGetResponse,
    TuneInfoResult,
    TuneMethodsGetResponse,
    TunesListResponse,
)
from genai.schemas.tunes_params import (
    CreateTuneParams,
    DownloadAssetsParams,
    TunesListParams,
)
from genai.services.service_interface import ServiceInterface
from genai.utils.service_utils import _get_service

logger = logging.getLogger(__name__)


class TuneManager:
    """Class for managing tunes on the server."""

    @staticmethod
    def list_tunes(
        credentials: Credentials = None, service: ServiceInterface = None, params: TunesListParams = None
    ) -> TunesListResponse:
        """List all tunes on the server.

        Args:
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.
            params (TunesListParams): Parameters for listing tunes.

        Returns:
            TunesListResponse: Response from the server.
        """
        service = _get_service(credentials, service)
        try:
            response = service._tunes.list_tunes(params=params)

            if response.status_code == 200:
                response = response.json()
                responses = TunesListResponse(**response)
                return responses
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def get_tune(tune_id: str, credentials: Credentials = None, service: ServiceInterface = None) -> TuneGetResponse:
        """Get a tune from the server.

        Args:
            tune_id: ID of the tune to fetch from the server.
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.

        Returns:
            TuneGetResponse: Response from the server.
        """
        service = _get_service(credentials, service)
        try:
            response = service._tunes.get_tune(tune_id=tune_id)
            if response.status_code == 200:
                response = response.json()
                responses = TuneGetResponse(**response)
                return responses.results
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def create_tune(
        credentials: Credentials = None, service: ServiceInterface = None, params: CreateTuneParams = None
    ) -> TuneInfoResult:
        """Create a new tune to be uploaded to the server.

        Args:
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.
            params (CreateTuneParams): Parameters for creating tunes.

        Returns:
            TuneInfoResult: Response from the server.
        """
        # TODO: check if the params.method_id is valid listing the tune models list

        if params.method_id == "mpt" and (params.parameters.init_method or params.parameters.init_text):
            raise GenAiException(
                "When using method_id 'mpt' you cannot use init_method or "
                "init_text, those are only for 'pt' (Prompt Tuning) method_id."
            )

        if params.task_id not in ["generation", "classification", "summarization"]:
            raise GenAiException(
                "The task_id must be one of the following: 'generation', 'classification' or 'summarization'."
            )

        service = _get_service(credentials, service)
        try:
            response = service._tunes.create_tune(params=params)
            if response.status_code == 200:
                response = response.json()
                responses = TuneInfoResult(**response["results"])
                return responses
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def delete_tune(tune_id: str, credentials: Credentials = None, service: ServiceInterface = None) -> dict:
        """Deletes a tune from the server.

        Args:
            tune_id: ID of the tune to delete from the server.
            credentials (Credentials, optional): Credentials object. Defaults to None.
                If not providec, service must be provided.
            service (ServiceInterface, optional): ServiceInterface object. Defaults to None.
                If not provided, credentials must be provided.

        Returns:
            dict: Response from the server.
        """
        service = _get_service(credentials, service)
        try:
            response = service._tunes.delete_tune(tune_id=tune_id)
            if response.status_code == 204:
                return {"status": "success"}
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def get_tune_methods(credentials: Credentials) -> TuneMethodsGetResponse:
        """Get list of tune methods.

        Returns:
            TuneMethodsGetResponse: Response from the server
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
        try:
            response = service._tunes.get_tune_methods()
            if response.status_code == 200:
                response = response.json()
                responses = TuneMethodsGetResponse(**response)
                return responses.results
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)

    @staticmethod
    def get_filename(params: DownloadAssetsParams):
        if params.content == "encoder":
            return f"{params.id}.pt"
        elif params.content == "logs":
            return f"{params.id}.jsonl"
        else:
            raise GenAiException("Input for 'content' must either be 'encoder' or 'logs'")

    @staticmethod
    def get_complete_path(output_path, filename):
        if output_path == "tune_assets":
            parent_path = pathlib.Path(__file__).parent.resolve()
            output_path = os.path.join(parent_path, output_path)
        if not (os.path.exists(output_path) and os.path.isdir(output_path)):
            os.makedirs(output_path)
        return os.path.join(output_path, filename)

    @staticmethod
    def download_tune_assets(credentials: Credentials, params: DownloadAssetsParams, output_path="tune_assets") -> dict:
        """Download tune asset (available only for completed tunes)

        Args:
            params (DownloadAssetsParams): Parameters for downloading tune assets.
            output_path (str): Output directory for tune assets file. Path is relative to services directory.

        Returns:
            dict: Response from the server.
        """

        filename = TuneManager.get_filename(params)

        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

        try:
            response = service._tunes.download_tune_assets(params=params)
            if response.status_code == 200:
                path = TuneManager.get_complete_path(output_path, filename)
                with open(path, "wb") as f:
                    return f.write(response.content)
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)
