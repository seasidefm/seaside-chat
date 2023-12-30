import json
import logging
from typing import Dict, Union, List, Set

from pydantic_core import ValidationError
from websockets.server import WebSocketServerProtocol

from app_types.actions import SocketMessage, MessageType
from app_types.chat_message import ChatMessage

# Custom types
WebSocketConnection = Dict[str, Union[WebSocketServerProtocol, List[str]]]


class ChatService:
    def __init__(self):
        # Dictionary to store WebSocket connections and their subscribed topics
        self.connections: Dict[str, WebSocketConnection] = {}

        # Dictionary to map topics to connection IDs
        self.topic_subscriptions: Dict[str, Set[str]] = {}

    def cleanup_socket(self, socket_id: str):
        del self.connections[socket_id]
        for topic in self.connections[socket_id]["topics"]:
            self.topic_subscriptions[topic].discard(socket_id)

    async def publish_to_topic(self, topic: str, message: SocketMessage):
        subscriptions = self.topic_subscriptions.get(topic, set())
        logging.info("Publishing to %s - %s", topic, message)

        for sub in subscriptions:
            await self.connections[sub]["websocket"].send(message.model_dump_json())

    async def process_message(self, websocket: WebSocketServerProtocol):
        connection_id = str(websocket.id)
        async for message in websocket:
            try:
                parsed = SocketMessage(**json.loads(message))
                match parsed.message_type:
                    case MessageType.ChatConnect:
                        logging.info(
                            f"Chat connection for ws:{websocket.id} for {parsed.topic}"
                        )
                        self.connections[connection_id] = {
                            "websocket": websocket,
                            "topics": {parsed.topic},
                        }

                        existing_subscriptions = self.topic_subscriptions.get(
                            parsed.topic, set()
                        )
                        self.topic_subscriptions[parsed.topic] = {
                            *existing_subscriptions,
                            connection_id,
                        }

                        logging.info(self.connections)

                    case MessageType.NewMessage:
                        message_payload = ChatMessage(**parsed.payload)

                        # Act on message content if desired...
                        print(
                            f"{message_payload.sent_by_username}: {message_payload.content}"
                        )

                        new_message = SocketMessage(
                            topic=parsed.topic,
                            message_type="new_message",
                            payload=message_payload.model_dump(),
                        )

                        # ACCESS ALL SUBSCRIBED CLIENTS HERE
                        await self.publish_to_topic(parsed.topic, new_message)

                    case _:
                        logging.warning(
                            f"Received unknown message type {parsed.message_type} - skipping!"
                        )
            except ValidationError as ve:
                print(message)
                logging.error(ve)

            except Exception as e:
                print(e.__class__)
                print(e)
                logging.error(e)

        # After the socket closes, for good or ill
        logging.info("Socket %s closed, removing from memory", connection_id)
        self.cleanup_socket(connection_id)
