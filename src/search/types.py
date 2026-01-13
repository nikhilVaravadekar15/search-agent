import datetime
from enum import StrEnum
from typing import Dict, Optional
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
    content: str
    error_message: str
    sources: List[Dict]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class APIRequest(BaseModel):
    query: str


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SseMode(StrEnum):
    METADATA = "metadata"
    THINKING = "thinking"
    RESPONSE = "response"
    ERROR = "error"
    DONE = "done"


class SseMessageType(StrEnum):
    CHUNK = "chunk"
    DONE = "done"
    CANCELLED = "cancelled"
    ERROR = "error"


class Source(BaseModel):
    title: str
    url: HttpUrl
    description: Optional[str]


class CompleteSource(Source):
    content: Optional[str]


class SseEvent(BaseModel):
    mode: SseMode
    message: str
    context: Optional[Dict] = None
    thread_id: UUID
    message_id: UUID
