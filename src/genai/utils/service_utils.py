from genai.exceptions.genai_exception import GenAiException
from genai.services import ServiceInterface


def _get_service(credentials, service):
    if credentials is None and service is None:
        raise GenAiException(ValueError("Credentials or ServiceInterface must be provided."))
    if credentials is not None and service is not None:
        raise GenAiException(ValueError("Provide exactly one of Credentials or ServiceInterface but not both."))
    if credentials is not None:
        service = ServiceInterface(service_url=credentials.api_endpoint, api_key=credentials.api_key)
    return service
