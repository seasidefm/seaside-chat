import dataclasses
import enum
import typing

from pydantic import BaseModel


SocketMessageType = typing.Literal["chat_connect", "new_message", "reply_message"]


class MessageType(str, enum.Enum):
    ChatConnect = "chat_connect"
    NewMessage = "new_message"
    ReplyMessage = "reply_message"


class SocketMessage(BaseModel):
    message_type: SocketMessageType
    payload: dict

