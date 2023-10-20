import unittest

import pytest

from genai.schemas import GenerateParams, ReturnOptions
from genai.utils.request_utils import sanitize_params

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate

SERVICE_URL = "https://workbench-api.res.ibm.com"
KEY = "pak-"


@pytest.mark.unit
class TestServiceUtils(unittest.TestCase):
    def test_sanitize_params_with_params(self):
        input_genParams = GenerateParams(decoding_method="greedy", return_options=ReturnOptions(input_text=True))

        expected_genParams = {"decoding_method": "greedy", "return_options": {"input_text": True}}

        sanitized_dict = sanitize_params(input_genParams)
        self.assertEqual(expected_genParams, sanitized_dict)
