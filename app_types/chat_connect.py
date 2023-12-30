import uuid

from pydantic import BaseModel, Field


def get_uuid():
    return str(uuid.uuid4())


class ChatConnect(BaseModel):
    id: str = Field(default_factory=get_uuid)
    user_id: str
    channel: str
