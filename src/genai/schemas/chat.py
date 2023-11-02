from enum import Enum
from typing import Literal

from pydantic import BaseModel


class ChatRole(str, Enum):
    user = "user"
    system = "system"
    assistant = "assistant"


class BaseMessage(BaseModel):
    role: ChatRole
    content: str


class HumanMessage(BaseMessage):
    role: Literal[ChatRole.user] = ChatRole.user


class SystemMessage(BaseMessage):
    role: Literal[ChatRole.system] = ChatRole.system


class AIMessage(BaseMessage):
    role: Literal[ChatRole.assistant] = ChatRole.assistant
