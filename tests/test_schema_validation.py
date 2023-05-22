import logging

import pytest

from genai.schemas.responses import (
    GenerateResponse,
    GenerateResult,
    HistoryResponse,
    HistoryResult,
    HistoryResultRequest,
    TermsOfUse,
    TokenizeResponse,
    TokenizeResult,
)
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestSchemas:
    def setup_method(self):
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    def _validate_extra_field(self, input_dict, model_type):
        """

        Args:
            input_dict (_type_): _description_
            model_type (_type_): _description_

        Returns:
            bool: _description_
        """
        logger.debug("Checking that {model_type.__name__} accepts extra parameters correctly")
        # Add extra field to input dict
        input_dict["extra_field"] = "this_is_an_extra_field"
        result = model_type(**input_dict)

        assert (
            f"{model_type.__name__}" in self.caplog.text
        ), f"Warning for {model_type.__name__} should be raised for extra field"
        assert (
            result.extra_field == "this_is_an_extra_field"
        ), f"Extra field in {model_type.__name__} should be accessable and set correctly"

    def test_log_warning_thrown_on_extra_field(self, caplog):
        """This test checks that the schemas within genai.schemas.responses
        all raise a logging WARNING if an extra field is detected, whilst also
        allowing said extra fields through into the model output.
        Args:
            caplog (Generator[LogCaptureFixture, None, None]): The Logging capture during the test
        """
        self.caplog = caplog
        self.caplog.set_level(logging.WARNING)

        # Test Generate Result
        generate_example = SimpleResponse.generate(model=self.model, inputs=self.inputs)
        self._validate_extra_field(generate_example, GenerateResponse)
        self._validate_extra_field(generate_example["results"][0], GenerateResult)

        tokenize_example = SimpleResponse.tokenize(model=self.model, inputs=self.inputs)
        self._validate_extra_field(tokenize_example, TokenizeResponse)
        self._validate_extra_field(tokenize_example["results"][0], TokenizeResult)

        history_example = SimpleResponse.history()
        self._validate_extra_field(history_example, HistoryResponse)
        self._validate_extra_field(history_example["results"][0], HistoryResult)
        self._validate_extra_field(history_example["results"][0]["request"], HistoryResultRequest)

        tou_example = SimpleResponse.terms_of_use()
        self._validate_extra_field(tou_example, TermsOfUse)
