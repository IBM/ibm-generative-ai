import unittest

import pytest

from genai.schemas import GenerateParams, ReturnOptions
from genai.services import ServiceInterface

# API Reference : https://workbench.res.ibm.com/docs/api-reference#generate

SERVICE_URL = "https://workbench-api.res.ibm.com/v1/"
KEY = "pak-"


@pytest.mark.unit
class TestServiceUtils(unittest.TestCase):
    def test_sanitize_params_with_params(self):
        input_genParams = GenerateParams(
            decoding_method="greedy", temperature=1.0, return_options=ReturnOptions(input_text=True)
        )

        expected_genParams = {"decoding_method": "greedy", "temperature": 1.0, "return_options": {"input_text": True}}

        sanitized_dict = ServiceInterface._sanitize_params(input_genParams)
        self.assertEqual(expected_genParams, sanitized_dict)

    def test_sanitize_params_with_dict(self):
        # TODO : Confirm what approach we want to have for user passing dict

        # Test with dictionary
        # input_dict = {
        #     "fieldA": None,
        #     "fieldB": None,
        #     "returns_options": "something",
        # }

        # expected_dict = {
        #     "return": "something",
        # }

        # sanitized_dict = sanitize_params(input_dict)
        # self.assertEqual(expected_dict, sanitized_dict)
        pass
