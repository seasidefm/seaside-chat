import asyncio
import json
import os
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Dict, Union, List, Set

from pydantic import ValidationError
from websockets.server import serve, WebSocketServerProtocol
from colorlog import ColoredFormatter
from dotenv import load_dotenv

from app_types.actions import SocketMessage, MessageType
from app_types.chat_connect import ChatConnect
from app_types.chat_message import ChatMessage

load_dotenv()
host = os.getenv("HOST", "localhost")
port = os.getenv("PORT", 8765)


def setup_logger():
    log_format = (
        "%(asctime)s [%(log_color)s%(levelname)s%(reset)s] %(module)s - %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure the logger to write logs to a file
    file_handler = TimedRotatingFileHandler("app.log", when="midnight", backupCount=7)
    file_handler.setFormatter(ColoredFormatter(log_format, datefmt=date_format))
    logging.getLogger().addHandler(file_handler)

    # Configure the logger to write logs to stdout with colors
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(ColoredFormatter(log_format, datefmt=date_format))
    logging.getLogger().addHandler(stdout_handler)

    # Set the overall logging level to INFO
    logging.getLogger().setLevel(logging.INFO)


# Call the setup_logger function to configure the logger
setup_logger()

# Define a type for WebSocket connections
WebSocketConnection = Dict[str, Union[WebSocketServerProtocol, List[str]]]

# Dictionary to store WebSocket connections and their subscribed topics
connections: Dict[str, WebSocketConnection] = {}

# Dictionary to map topics to connection IDs
topic_subscriptions: Dict[str, Set[str]] = {}


def cleanup_socket(socket_id: str):
    del connections[socket_id]
    for topic in connections[socket_id]["topics"]:
        topic_subscriptions[topic].discard(socket_id)


async def publish_to_topic(topic: str, message: SocketMessage):
    subscriptions = topic_subscriptions.get(topic, set())
    logging.info("Publishing to %s - %s", topic, message)
    for sub in subscriptions:
        await connections[sub]["websocket"].send(message.model_dump_json())


async def process_message(websocket: WebSocketServerProtocol):
    connection_id = str(websocket.id)
    async for message in websocket:
        try:
            parsed = SocketMessage(**json.loads(message))
            match parsed.message_type:
                case MessageType.ChatConnect:
                    logging.info(
                        f"Chat connection for ws:{websocket.id} for {parsed.topic}"
                    )
                    connections[connection_id] = {
                        "websocket": websocket,
                        "topics": {parsed.topic},
                    }

                    existing_subscriptions = topic_subscriptions.get(
                        parsed.topic, set()
                    )
                    topic_subscriptions[parsed.topic] = {
                        *existing_subscriptions,
                        connection_id,
                    }

                    logging.info(connections)

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
                    await publish_to_topic(parsed.topic, new_message)

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
    cleanup_socket(connection_id)


async def main():
    async with serve(process_message, host, port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
