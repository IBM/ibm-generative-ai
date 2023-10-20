import pytest
from pydantic import BaseModel, ValidationError

from genai.utils.general import to_model_instance


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
