import re
from warnings import warn


class Credentials:
    DEFAULT_API = "https://workbench-api.res.ibm.com"

    def __init__(
        self,
        api_key: str,
        api_endpoint: str = DEFAULT_API,
    ):
        """
        Instansiate the credentials object

        Args:
            api_key (str): The GENAI API Key
            api_endpoint (str, optional): GENAI API Endpoint. Defaults to DEFAULT_API.
        """
        if api_key is None:
            raise ValueError("api_key must be provided")
        self.api_key = api_key
        if api_endpoint is None:
            raise ValueError("api_endpoint must be provided")
        self.api_endpoint = api_endpoint.rstrip("/")
        self._remove_api_endpoint_version()

    def _remove_api_endpoint_version(self) -> None:
        [api, *version] = re.split(r"(/v\d+$)", self.api_endpoint, maxsplit=1)
        if version:
            warn(
                DeprecationWarning(
                    f"The 'api_endpoint' property should not contain any explicit API version"
                    f"(rename it from '{self.api_endpoint}' to just '{api}')"
                )
            )
            self.api_endpoint = api
