class Credentials:
    DEFAULT_API = "https://workbench-api.res.ibm.com/v1"

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

        self.api_key = api_key
        self.api_endpoint = api_endpoint
