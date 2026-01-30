import datetime
from enum import StrEnum
from typing import Annotated, Any, Dict, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


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


class FlowType(StrEnum):
    NORMAL = "normal"
    REGENERATE = "regenerate"
    FOLLOW_UP = "follow_up"


class BaseFlow(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None


class NormalFlow(BaseFlow):
    type: Literal[FlowType.NORMAL]


class RegenerateFlow(BaseFlow):
    type: Literal[FlowType.REGENERATE]
    um_id: UUID


class FollowUpFlow(BaseFlow):
    type: Literal[FlowType.FOLLOW_UP]
    text: str


Flow = Annotated[
    Union[NormalFlow, RegenerateFlow, FollowUpFlow],
    Field(discriminator="type"),
]


class APIRequest(BaseModel):
    query: str


class ConversationAPIRequest(APIRequest):
    parent_message_id: Optional[UUID]
    context: Flow


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
    meta: Optional[Dict] = None
    thread_id: UUID
    track_id: UUID
    um_id: UUID
    aim_id: UUID
