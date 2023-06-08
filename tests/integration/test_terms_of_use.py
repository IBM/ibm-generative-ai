import pytest

from genai import Metadata


@pytest.mark.integration
class TestTermsOfUseIntegration:
    def test_accept_tou(self, credentials):
        metadata = Metadata(credentials)

        tou_response = metadata.accept_terms_of_use()
        assert tou_response.results.tou_accepted is True
