from urllib3.util import parse_url


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
        self.remove_version()

    def remove_version(self) -> None:
        parsed_url = parse_url(self.api_endpoint)

        if parsed_url.path and "/v" in parsed_url.path:
            self.api_endpoint = self.api_endpoint.split("/v")[0]
            print("Warning: Api_endpoint should not contain any version, removing it")
