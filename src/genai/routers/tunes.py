from genai.exceptions import GenAiException
from genai.schemas.tunes_params import CreateTuneParams, TunesListParams
from genai.services.request_handler import RequestHandler


class TunesRouter:
    TUNES = "/tunes"

    def __init__(self, service_url: str, api_key: str) -> None:
        self.service_url = service_url.rstrip("/")
        self.key = api_key

    def list_tunes(self, params: TunesListParams):
        from genai.services import ServiceInterface  # circular import

        """List all tunes on the server.
        Returns:
            ListTunesResponse: json from querying for tunes list.
        """
        try:
            params = ServiceInterface._sanitize_params(params)
            endpoint = self.service_url + TunesRouter.TUNES
            return RequestHandler.get(endpoint, key=self.key, parameters=params)
        except Exception as e:
            raise GenAiException(e)

    def get_tune(self, tune_id: str):
        """Get a given tune from the server.
        Returns:
            TuneGetResponse: json from querying for tune with the given ID.
        """
        try:
            endpoint = self.service_url + TunesRouter.TUNES + "/" + tune_id
            return RequestHandler.get(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def create_tune(self, params: CreateTuneParams):
        from genai.services import ServiceInterface  # circular import

        """Create a new tune.
        Returns:
            TuneInfoResult: json with info about the newly generated tune.
        """
        try:
            params = ServiceInterface._sanitize_params(params)
            endpoint = self.service_url + TunesRouter.TUNES
            return RequestHandler.post(endpoint, key=self.key, payload=params)
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
            return RequestHandler.delete(endpoint, key=self.key, parameters=tune_id)
        except Exception as e:
            raise GenAiException(e)
