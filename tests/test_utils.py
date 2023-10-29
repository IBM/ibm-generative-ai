from re import Match

import pytest
from pydantic import BaseModel, ValidationError

from genai.utils.general import to_model_instance
from tests.utils import match_endpoint


@pytest.mark.unit
class TestUtils:
    def test_cast_to_model(self):
        class Company(BaseModel):
            name: str

        model = Company(name="IBM")
        assert model == to_model_instance(model, Company)
        assert model is not to_model_instance(model, Company)

        assert model == to_model_instance({"name": model.name}, Company)

        with pytest.raises(ValueError):
            to_model_instance([], Company)
        with pytest.raises(ValidationError):
            to_model_instance({}, Company)

    def test_match_endpoint(self):
        match_ep = match_endpoint("v1/generate")
        url = "http://service_url/v1/tokenize"
        assert match_ep.match(url) is None

        match_ep = match_endpoint("v1/generate", "path", query_params={"parameter": 20, "test": "test"})
        url = "http://service_url/v1/generate/path?parameter=20&test=test"
        assert isinstance(match_ep.match(url), Match) is True
