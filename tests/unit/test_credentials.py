import pytest

from genai.credentials import Credentials


@pytest.mark.unit
class TestCredentials:
    def test_version(self):
        with pytest.raises(ValueError):
            Credentials(api_key="GENAI_API_KEY", api_endpoint="https://bam-api.res.ibm.com/v1/")

    @pytest.mark.parametrize("api_endpoint", ["https://example.com/a/b/c", "https://example.com"])
    def test_correct_versions(self, api_endpoint: str):
        Credentials(api_key="GENAI_API_KEY", api_endpoint=api_endpoint)

    def test_prevent_leaking_api_key(self):
        api_key = "MY_SECRET_API_KEY"
        credentials = Credentials(api_key=api_key, api_endpoint="https://example.com")
        assert api_key not in str(credentials)
        assert api_key not in credentials.model_dump_json()
