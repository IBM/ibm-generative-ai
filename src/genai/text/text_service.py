from typing import Optional, Type

from genai._utils.api_client import ApiClient
from genai._utils.base_service import (
    BaseService,
    BaseServiceConfig,
    BaseServiceServices,
)
from genai.text.chat.chat_generation_service import ChatService
from genai.text.embedding.embedding_service import EmbeddingService
from genai.text.generation.generation_service import GenerationService
from genai.text.moderation.moderation_service import ModerationService
from genai.text.tokenization.tokenization_service import TokenizationService

__all__ = ["TextService", "BaseServices"]


class BaseServices(BaseServiceServices):
    """Appropriate services used by the Text Service"""

    GenerationService: Type[GenerationService] = GenerationService
    TokenizationService: Type[TokenizationService] = TokenizationService
    ChatService: Type[ChatService] = ChatService
    ModerationService: Type[ModerationService] = ModerationService
    EmbeddingService: Type[EmbeddingService] = EmbeddingService


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
