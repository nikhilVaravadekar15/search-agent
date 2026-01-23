import datetime
from enum import StrEnum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class ConversationThread(BaseModel):
    id: UUID
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    parent_id: Optional[UUID] = None
    content: Optional[str] = None
    error_message: Optional[str] = None
    follow_context: Optional[Dict] = None
    sources: Optional[list[dict]] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class FollowType(StrEnum):
    REGENERATE = "regenerate"
    FOLLOW_UP = "follow_up"


class FollowContext(BaseModel):
    type: FollowType
    from_message_id: UUID
    text: str
    start: Optional[int] = None
    end: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None


class APIRequest(BaseModel):
    query: str


class ConversationAPIRequest(APIRequest):
    query: str
    parent_message_id: Optional[UUID] = None
    follow_context: Optional[FollowContext] = None


class APICancelRequest(BaseModel):
    track_id: UUID


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SseMode(StrEnum):
    METADATA = "metadata"
    THINKING = "thinking"
    RESPONSE = "response"
    ERROR = "error"


class SseMessageType(StrEnum):
    CHUNK = "chunk"
    DONE = "done"
    CANCELLED = "cancelled"
    ERROR = "error"


class Source(BaseModel):
    title: str
    link: HttpUrl
    snippet: Optional[str]


class CompleteSource(Source):
    content: Optional[str]


class CustomMessage(BaseModel):
    message: Optional[str] = None
    meta: Optional[Any] = None


class SseEvent(BaseModel):
    mode: SseMode
    message: str
    context: Optional[Dict] = None
    thread_id: UUID
    track_id: UUID
    message_id: UUID
