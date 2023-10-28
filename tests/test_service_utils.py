import unittest

import pytest

from genai.schemas import GenerateParams, ReturnOptions
from genai.services import ServiceInterface
from genai.utils.request_utils import match_endpoint, sanitize_params

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

    def test_match_endpoint(self):
        match_ep = match_endpoint(ServiceInterface.GENERATE)
        url = "http://service_url/v1/generate"
        assert match_ep.match(url)

        match_ep = match_endpoint(ServiceInterface.GENERATE, query_params={"parameter": 20, "test": "test"})
        url = "http://service_url/v1/generate?parameter=20&test=test"
        assert match_ep.match(url)
