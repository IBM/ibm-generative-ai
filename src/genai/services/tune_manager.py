import logging

from genai.credentials import Credentials
from genai.exceptions.genai_exception import GenAiException
from genai.schemas.responses import TuneGetResponse, TuneInfoResult, TunesListResponse
from genai.schemas.tunes_params import CreateTuneParams, TunesListParams
from genai.services.service_interface import ServiceInterface

logger = logging.getLogger(__name__)


class TuneManager:
    """Class for managing tunes on the server."""

    @staticmethod
    def list_tunes(credentials: Credentials, params: TunesListParams) -> TunesListResponse:
        """List all tunes on the server.

        Args:
            params (TunesListParams): Parameters for listing tunes.

        Returns:
            TunesListResponse: Response from the server.
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
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
    def get_tune(credentials: Credentials, tune_id: str) -> TuneGetResponse:
        """Get a tune from the server.

        Args:
            tune_id: ID of the tune to fetch from the server.

        Returns:
            TuneInfoResult
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
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
    def create_tune(credentials: Credentials, params: CreateTuneParams) -> TuneInfoResult:
        """Create a new tune to be uploaded to the server.

        Args:
            params (CreateTuneParams): Parameters for creating tunes.

        Returns:
            TuneInfoResult: Response from the server.
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
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
    def delete_tune(credentials: Credentials, tune_id: str) -> dict:
        """Deletes a tune from the server.

        Args:
            tune_id: ID of the tune to delete from the server.

        Returns:
            dict: Response from the server.
        """
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
        try:
            response = service._tunes.delete_tune(tune_id=tune_id)
            if response.status_code == 204:
                return {"status": "success"}
            else:
                raise GenAiException(response)
        except Exception as e:
            raise GenAiException(e)
