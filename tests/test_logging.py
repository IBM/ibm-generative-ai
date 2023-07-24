import logging

import pytest

from genai import Credentials, Model
from genai.schemas import GenerateParams

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


@pytest.mark.unit
class TestLogging:
    def test_no_leaked_logs(self, caplog):
        credentials = Credentials("GENAI_API_KEY")
        params = GenerateParams()
        Model("google/flan-ul2", params=params, credentials=credentials)

        assert len(caplog.records) == 0

    def test_basic_logs(self, caplog):
        caplog.set_level(logging.DEBUG)

        credentials = Credentials("GENAI_API_KEY")
        params = GenerateParams()
        Model("google/flan-ul2", params=params, credentials=credentials)

        assert "google/flan-ul2" in caplog.text
