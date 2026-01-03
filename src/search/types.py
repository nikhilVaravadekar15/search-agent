import datetime
from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
