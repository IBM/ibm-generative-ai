from typing import Optional

from .responses import GenerateStreamResponse, ModerationResult


class ApiGenerateStreamResponse(GenerateStreamResponse):
    moderation: Optional[ModerationResult] = None
