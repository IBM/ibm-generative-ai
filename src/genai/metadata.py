import logging

from genai.credentials import Credentials
from genai.exceptions import GenAiException
from genai.schemas.history_params import HistoryParams
from genai.schemas.responses import HistoryResponse, TermsOfUse
from genai.services import ServiceInterface

logger = logging.getLogger(__name__)


class Metadata:
    DEFAULT_MAX_PROMPTS = 5

    def __init__(self, credentials: Credentials):
        """Get's metadata for service backing the Model class.

        Args:
            credentials (Credentials): The API Credentials
        """

        logger.debug(f"Metadata Created: api_endpoint: {credentials.api_endpoint}")
        self.service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)

    def accept_terms_of_use(self) -> TermsOfUse:
        """Accepts the terms of use on GENAI.

        Returns:
            TermsOfUse: Terms of Use Data
        """

        try:
            tou_response = self.service.terms_of_use(True)

            if tou_response.status_code == 200:
                tou_data = TermsOfUse(**tou_response.json())
                return tou_data
            else:
                raise GenAiException(tou_response)
        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)

    def get_history(self, params: HistoryParams = HistoryParams()) -> HistoryResponse:
        """The requests endpoint provides the ability to retrieve past generation requests
           and responses returned by the given models.
           Items are returned in reverse chronological order.

        Args:
            params (HistoryParams): History parameters

        Returns:
            HistoryResponse: The History of requests and responses
        """

        try:
            history_response = self.service.history(params)

            if history_response.status_code == 200:
                history_data = HistoryResponse(**history_response.json())
                return history_data
            else:
                raise GenAiException(history_response)
        except GenAiException as me:
            raise me
        except Exception as ex:
            raise GenAiException(ex)
