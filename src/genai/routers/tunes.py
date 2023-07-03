from genai.exceptions import GenAiException
from genai.services import ServiceInterface

<<<<<<< HEAD
from genai.schemas.tunes_params import CreateTuneParams, TunesListParams
=======
from genai.schemas import (
    CreateTuneParams,
    TunesListParams,
)
>>>>>>> 41b8679 (fix: fixed tunes router)
from genai.services.request_handler import RequestHandler


class TunesRouter:
    TUNES = "/tunes"

    def __init__(self, service_url: str, api_key: str) -> None:
        self.service_url = service_url.rstrip("/")
        self.key = api_key

    def list_tunes(self, params: TunesListParams):
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
<<<<<<< HEAD
            endpoint = self.service_url + TunesRouter.TUNES + "/" + tune_id
=======
            endpoint = self.service_url + TunesRouter.TUNES + tune_id
>>>>>>> 41b8679 (fix: fixed tunes router)
            return RequestHandler.get(endpoint, key=self.key)
        except Exception as e:
            raise GenAiException(e)

    def create_tune(self, params: CreateTuneParams):
        """Create a new tune.
        Returns:
            TuneInfoResult: json with info about the newly generated tune.
        """
        try:
            params = ServiceInterface._sanitize_params(params)
<<<<<<< HEAD
            endpoint = self.service_url + TunesRouter.TUNES
=======
            endpoint = self.service_url + TunesRouter.TUNES + TunesRouter.TUNES
>>>>>>> 41b8679 (fix: fixed tunes router)
            return RequestHandler.post(endpoint, key=self.key, payload=params)
        except Exception as e:
            raise GenAiException(e)

    def delete_tune(self, tune_id: str):
<<<<<<< HEAD
        """Delete a tune from the server.

        Args:
            tune_id (str): Id of the tune to be deleted.

        Returns:
            Any: json with info about the deleted tune.
        """
=======
        """Deletes a tune from the server."""
>>>>>>> 41b8679 (fix: fixed tunes router)
        try:
            endpoint = self.service_url + TunesRouter.TUNES + "/" + tune_id
            return RequestHandler.delete(endpoint, key=self.key, parameters=tune_id)
        except Exception as e:
            raise GenAiException(e)
<<<<<<< HEAD
=======
        
>>>>>>> 41b8679 (fix: fixed tunes router)
