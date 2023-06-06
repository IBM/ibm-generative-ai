from unittest.mock import MagicMock, patch

import pytest

from genai import Credentials, Metadata
from genai.schemas.responses import HistoryResponse, TermsOfUse
from tests.assets.response_helper import SimpleResponse


@pytest.mark.unit
class TestMetadata:
    @patch("genai.services.ServiceInterface.terms_of_use")
    def test_accept_TOU(self, mock_requests):
        """Tests that we can accept the TOU"""

        TOU_RESPONSE = SimpleResponse.terms_of_use()

        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = TOU_RESPONSE
        mock_requests.return_value = mock_response

        # Build up our Model Object
        creds = Credentials("TEST_API_KEY")

        # Instantiate the GENAI Proxy Object
        model_meta = Metadata(creds)

        tou_response = model_meta.accept_terms_of_use()
        original_tou = TermsOfUse(**TOU_RESPONSE)
        assert tou_response == original_tou

    @patch("genai.services.ServiceInterface.history")
    def test_history(self, mock_requests):
        """Tests that we can get the History"""

        HISTORY_RESPONSE = SimpleResponse.history()

        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = HISTORY_RESPONSE
        mock_requests.return_value = mock_response

        # Build up our Model Object
        creds = Credentials("TEST_API_KEY")

        # Instantiate the GENAI Proxy Object
        model_meta = Metadata(creds)

        history_response = model_meta.get_history()
        original_history_response = HistoryResponse(**HISTORY_RESPONSE)
        assert history_response == original_history_response
