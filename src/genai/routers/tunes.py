from genai.exceptions import GenAiException
from genai.schemas.tunes_params import (
    CreateTuneParams,
    DownloadAssetsParams,
    TunesListParams,
)
from genai.services.request_handler import RequestHandler
from genai.utils.request_utils import sanitize_params


class TunesRouter:
    TUNES = "/v1/tunes"
    TUNE_METHODS = "/v1/tune_methods"

    def __init__(self, service_url: str, api_key: str) -> None:
        self.service_url = service_url.rstrip("/")
        self.key = api_key

    def list_tunes(self, params: TunesListParams = None):
        """List all tunes on the server.

        Args:
            params (TunesListParams, optional): Parameters for the tune list.

        Returns:
            Any: json from querying for tune list.
        """
        try:
            params = sanitize_params(params)
            endpoint = self.service_url + TunesRouter.TUNES
            return RequestHandler.get(endpoint, key=self.key, parameters=params)
        except Exception as e:
            raise GenAiException(e)

    def get_tune(self, tune_id: str):
        """Get a given tune from the server.

        Args:
            tune_id (str): Id of the tune to be retrieved.

        Returns:
            Any: json from querying for tune retrieval.
        """
        try:
            endpoint = self.service_url + TunesRouter.TUNES + "/" + tune_id
            return RequestHandler.get(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def create_tune(self, params: CreateTuneParams):
        """Create a new tune on the server.

        Args:
            params (CreateTuneParams): Parameters for the tune creation.

        Returns:
            Any: json with info about the created tune.
        """

        try:
            params = sanitize_params(params)
            endpoint = self.service_url + TunesRouter.TUNES
            return RequestHandler.post(endpoint, key=self.key, options=params)
        except Exception as e:
            raise GenAiException(e)

    def delete_tune(self, tune_id: str):
        """Delete a tune from the server.

        Args:
            tune_id (str): Id of the tune to be deleted.

        Returns:
            Any: json with info about the deleted tune.
        """
        try:
            endpoint = self.service_url + TunesRouter.TUNES + "/" + tune_id
            return RequestHandler.delete(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def get_tune_methods(self):
        """Get list of tune methods.

        Returns:
            Any: json with info about the available tune methods.
        """
        try:
            endpoint = self.service_url + self.TUNE_METHODS
            return RequestHandler.get(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def download_tune_assets(self, params: DownloadAssetsParams):
        """Download tune asset.

        Returns:
            Any: json with info about the downloaded tune asset.
        """
        try:
            endpoint = self.service_url + TunesRouter.TUNES + "/" + params.id + "/content/" + params.content
            return RequestHandler.get(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)
