from typing import Optional

from genai import Credentials
from genai.services import ServiceInterface
from genai.utils.service_utils import _get_service


class BaseService:
    _credentials: Credentials
    _api_service: ServiceInterface

    def __init__(self, *, credentials: Credentials, service: Optional[ServiceInterface] = None):
        self._credentials = credentials
        self._api_service = _get_service(credentials=credentials, service=service)
