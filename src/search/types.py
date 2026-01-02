import datetime
from uuid import UUID

from pydantic import BaseModel


class APIRequest(BaseModel):
    query: str


class CreateThreadResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
