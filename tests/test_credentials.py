import pytest

from genai import Credentials


@pytest.mark.unit
class TestCredentials:
    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_remove_version(self):
        credentials = Credentials(api_key="GENAI_API_KEY", api_endpoint="https://workbench-api.res.ibm.com/v1/")

        assert "/v1" not in credentials.api_endpoint

        credentials = Credentials(api_key="GENAI_API_KEY", api_endpoint="https://workbench-api.res.ibm.com/v2/ai/v12")

        assert credentials.api_endpoint == "https://workbench-api.res.ibm.com/v2/ai"
