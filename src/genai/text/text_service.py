from typing import Optional

from pydantic import BaseModel

from genai._utils.api_client import ApiClient
from genai._utils.service import (
    BaseService,
    BaseServiceConfig,
)
from genai.text.chat.chat_generation_service import ChatService as _ChatService
from genai.text.embedding.embedding_service import EmbeddingService as _EmbeddingService
from genai.text.generation.generation_service import GenerationService as _GenerationService
from genai.text.moderation.moderation_service import ModerationService as _ModerationService
from genai.text.tokenization.tokenization_service import TokenizationService as _TokenizationService

__all__ = ["TextService", "BaseServices"]


class BaseServices(BaseModel):
    """Appropriate services used by the Text Service"""

    GenerationService: type[_GenerationService] = _GenerationService
    TokenizationService: type[_TokenizationService] = _TokenizationService
    ChatService: type[_ChatService] = _ChatService
    ModerationService: type[_ModerationService] = _ModerationService
    EmbeddingService: type[_EmbeddingService] = _EmbeddingService


class TextService(BaseService[BaseServiceConfig, BaseServices]):
    """
    Class providing access to various text-related services.
    """

    Services = BaseServices

    def __init__(self, *, api_client: ApiClient, services: Optional[BaseServices] = None, **kwargs):
        super().__init__(api_client=api_client, **kwargs)

        if not services:
            services = self.Services()

        self.moderation = services.ModerationService(api_client=api_client)
        self.generation = services.GenerationService(api_client=api_client)
        self.tokenization = services.TokenizationService(api_client=api_client)
        self.chat = services.ChatService(api_client=api_client)
        self.embedding = services.EmbeddingService(api_client=api_client)
