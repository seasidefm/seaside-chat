import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


def get_uuid():
    return str(uuid.uuid4())


class ChatMessage(BaseModel):
    id: str = Field(default_factory=get_uuid)
    sent_by_id: str
    sent_by_username: str
    selected_color: str
    content: str
    sent: datetime = Field(default_factory=datetime.now)
    reply_thread_id: Optional[str] = None
