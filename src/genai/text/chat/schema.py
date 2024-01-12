from __future__ import annotations

from genai._generated.api import (
    BaseMessage,
    ChatRole,
    LengthPenalty,
    ModerationHAP,
    ModerationImplicitHate,
    ModerationParameters,
    ModerationStigma,
    RequestChatConversationIdRetrieveResponse,
    StopReason,
    TextChatCreateResponse,
    TextChatStreamCreateResponse,
    TextGenerationParameters,
    TextGenerationReturnOptions,
    TrimMethod,
)


class HumanMessage(BaseMessage):
    role: ChatRole = ChatRole.USER


class SystemMessage(BaseMessage):
    role: ChatRole = ChatRole.SYSTEM


class AIMessage(BaseMessage):
    role: ChatRole = ChatRole.ASSISTANT


__all__ = [
    "TextGenerationParameters",
    "TextGenerationReturnOptions",
    "TextChatCreateResponse",
    "TextChatStreamCreateResponse",
    "ChatRole",
    "BaseMessage",
    "AIMessage",
    "HumanMessage",
    "SystemMessage",
    "ModerationStigma",
    "ModerationHAP",
    "ModerationImplicitHate",
    "TrimMethod",
    "LengthPenalty",
    "StopReason",
    "ModerationParameters",
    "RequestChatConversationIdRetrieveResponse",
]
