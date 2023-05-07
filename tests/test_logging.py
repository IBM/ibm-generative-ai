import logging

import pytest

from genai import Credentials, Model
from genai.schemas import GenerateParams, ModelType

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


@pytest.mark.unit
class TestLogging:
    def test_no_leaked_logs(self, caplog):
        credentials = Credentials("GENAI_API_KEY")
        params = GenerateParams()
        Model(ModelType.FLAN_UL2, params=params, credentials=credentials)

        assert len(caplog.records) == 0

    def test_basic_logs(self, caplog):
        caplog.set_level(logging.DEBUG)

        credentials = Credentials("GENAI_API_KEY")
        params = GenerateParams()
        Model(ModelType.FLAN_UL2, params=params, credentials=credentials)
        # Enums are converted to strings slightly differently across python 3.9, 3.10 and 3.11
        assert any(x in caplog.text for x in [ModelType.FLAN_UL2, ModelType.FLAN_UL2.value, "ModelType.FLAN_UL2"])
