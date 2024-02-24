from typing import Optional

from pydantic import BaseModel

from genai._utils.api_client import ApiClient
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
)
from genai.text.experimental.classification import ClassificationService as _ClassificationService
from genai.text.experimental.rerank import RerankService as _RerankService
from genai.text.experimental.sentence_similarity import SentenceSimilarityService as _SentenceSimilarityService

__all__ = ["ExperimentalService", "BaseServices"]


class BaseServices(BaseModel):
    ClassificationService: type[_ClassificationService] = _ClassificationService
    RerankService: type[_RerankService] = _RerankService
    SentenceSimilarityService: type[_SentenceSimilarityService] = _SentenceSimilarityService


class ExperimentalService(BaseService[BaseServiceConfig, BaseServices]):
    """Text Experimental service which contains functionalities that are under development and thus can change."""

    Services = BaseServices

    @property
    def classification(self):
        # TODO: add deprecation warning once released
        return self._classification

    @property
    def rerank(self):
        # TODO: add deprecation warning once released
        return self._rerank

    @property
    def sentence_similarity(self):
        # TODO: add deprecation warning once released
        return self._sentence_similarity

    def __init__(self, *, api_client: ApiClient, services: Optional[BaseServices] = None, **kwargs):
        super().__init__(api_client=api_client, **kwargs)

        if not services:
            services = self.Services()

        self._classification = services.ClassificationService(api_client=api_client)
        self._rerank = services.RerankService(api_client=api_client)
        self._sentence_similarity = services.SentenceSimilarityService(api_client=api_client)
