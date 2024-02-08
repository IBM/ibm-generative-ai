import pytest

from genai.extensions.llama_index import LlamaIndexEmbeddingsInterface
from genai.schema import TextEmbeddingCreateEndpoint, TextEmbeddingParameters


@pytest.mark.integration
class TestLangChainEmbeddings:
    def setup_method(self):
        self.model_id = "sentence-transformers/all-minilm-l6-v2"

    @pytest.fixture
    def parameters(self):
        return TextEmbeddingParameters(truncate_input_tokens=True)

    @pytest.fixture
    def documents(self) -> list[str]:
        return ["First document", "Second document"]

    @pytest.mark.vcr
    def test_embedding(self, client, parameters, documents, get_vcr_responses_of):
        model = LlamaIndexEmbeddingsInterface(model_id=self.model_id, parameters=parameters, client=client)

        results = model.get_text_embedding_batch(documents)
        responses = get_vcr_responses_of(TextEmbeddingCreateEndpoint)

        for response, result in zip(responses, results):
            assert result == response["results"][0]

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_async_embedding(self, client, parameters, documents, get_vcr_responses_of):
        model = LlamaIndexEmbeddingsInterface(model_id=self.model_id, parameters=parameters, client=client)

        results = await model.aget_text_embedding_batch(documents)
        responses = get_vcr_responses_of(TextEmbeddingCreateEndpoint)

        for response, result in zip(responses, results):
            assert result == response["results"][0]
