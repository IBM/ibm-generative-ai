import re


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
        self.api_endpoint = api_endpoint
        self._remove_api_endpoint_version()

    def _remove_api_endpoint_version(self) -> None:
        has_version = re.search(r".\d$", self.api_endpoint)
        if has_version:
            self.api_endpoint = self.api_endpoint.rsplit("/v", 1)[0]
            print("Warning: Api_endpoint should not contain any version, removing it")
