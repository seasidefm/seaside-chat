import json
import logging
from typing import Dict, Union, List, Set

from pydantic_core import ValidationError
from websockets.server import WebSocketServerProtocol

from app_types.actions import SocketMessage, MessageType
from app_types.chat_message import ChatMessage

# Custom types
WebSocketConnection = Dict[str, Union[WebSocketServerProtocol, List[str]]]


from typing import Dict, Set
from websockets import WebSocketServerProtocol
from pydantic import ValidationError
import logging
import json


class ChatService:
    """
    A class representing a WebSocket-based chat service.

    Attributes:
    - connections: A dictionary to store WebSocket connections and their subscribed topics.
    - topic_subscriptions: A dictionary to map topics to connection IDs.

    Methods:
    - cleanup_socket(socket_id: str): Remove a WebSocket connection and its subscriptions from memory.
    - publish_to_topic(topic: str, message: SocketMessage): Publish a message to all connections subscribed to a topic.
    - process_message(websocket: WebSocketServerProtocol): Process incoming messages from a WebSocket connection.
    """

    def __init__(self):
        """
        Initialize a new instance of the ChatService class.
        """
        # Dictionary to store WebSocket connections and their subscribed topics
        self.connections: Dict[str, WebSocketConnection] = {}

        # Dictionary to map topics to connection IDs
        self.topic_subscriptions: Dict[str, Set[str]] = {}

    def cleanup_socket(self, socket_id: str):
        """
        Remove a WebSocket connection and its subscriptions from memory.

        Args:
        - socket_id (str): The ID of the WebSocket connection to be removed.
        """
        for topic in self.connections[socket_id]["topics"]:
            self.topic_subscriptions[topic].discard(socket_id)

        del self.connections[socket_id]

    async def publish_to_topic(self, topic: str, message: SocketMessage):
        """
        Publish a message to all connections subscribed to a topic.

        Args:
        - topic (str): The topic to which the message is published.
        - message (SocketMessage): The message to be published.
        """
        subscriptions = self.topic_subscriptions.get(topic, set())
        logging.info("Publishing to %s - %s", topic, message)

        for sub in subscriptions:
            await self.connections[sub]["websocket"].send(message.model_dump_json())

    async def process_message(self, websocket: WebSocketServerProtocol):
        """
        Process incoming messages from a WebSocket connection.

        Args:
        - websocket (WebSocketServerProtocol): The WebSocket connection to process messages for.
        """
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
