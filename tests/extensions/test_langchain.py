from unittest.mock import MagicMock, patch

import pytest

from genai import Credentials
from genai.schemas import GenerateParams, ModelType
from genai.schemas.responses import GenerateResponse
from genai.services import ServiceInterface
from tests.assets.response_helper import SimpleResponse


@pytest.mark.extension
class TestLangChain:
    def setup_method(self):
        self.service = ServiceInterface(service_url="SERVICE_URL", api_key="API_KEY")
        self.model = "google/ul2"
        self.inputs = ["Write a tagline for an alumni association: Together we"]

    @pytest.fixture
    def credentials(self):
        return Credentials("GENAI_APY_KEY")

    @pytest.fixture
    def params(self):
        return GenerateParams()

    @pytest.fixture
    def prompts(self):
        return ["Hi! How's the weather, eh?"]

    @patch("genai.services.RequestHandler.post")
    def test_langchain_interface(self, mocked_post_request, credentials, params, prompts):
        from genai.extensions.langchain import LangChainInterface

        GENERATE_RESPONSE = SimpleResponse.generate(model=ModelType.FLAN_UL2, inputs=prompts, params=params)
        expected_generated_response = GenerateResponse(**GENERATE_RESPONSE)

        response = MagicMock(status_code=200)
        response.json.return_value = GENERATE_RESPONSE
        mocked_post_request.return_value = response

        model = LangChainInterface(model=ModelType.FLAN_UL2, params=params, credentials=credentials)
        observed = model(prompts[0])
        assert observed == expected_generated_response.results[0].generated_text

    def test_prompt_translator(self):
        from langchain import PromptTemplate

        import genai.extensions.langchain  # noqa
        from genai.prompt_pattern import PromptPattern

        s = "My name is {name}. I work for {company}. I live in {city}."
        pt = PromptTemplate(input_variables=["name", "company", "city"], template=s)
        pattern = PromptPattern.langchain.from_template(pt)
        assert pattern.find_vars() == {"name", "company", "city"}
        ptemp = pattern.langchain.as_template()
        assert set(ptemp.input_variables) == {"name", "company", "city"}
        assert ptemp.template == s
