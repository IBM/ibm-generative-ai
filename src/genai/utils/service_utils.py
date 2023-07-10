from genai.credentials import Credentials
from genai.exceptions.genai_exception import GenAiException
from genai.services import ServiceInterface


def _check_credentials(credentials):
    if isinstance(credentials, ServiceInterface):
        service = credentials
    elif isinstance(credentials, Credentials):
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
    else:
        raise GenAiException("Credentials or ServiceInterface must be provided.")
    return service
