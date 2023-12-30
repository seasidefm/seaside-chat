import asyncio
import json
import os
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from websockets.server import serve, WebSocketServerProtocol
from colorlog import ColoredFormatter
from dotenv import load_dotenv

from app_types.actions import SocketMessage, MessageType
from app_types.chat_message import ChatMessage

load_dotenv()
host = os.getenv("HOST", "localhost")
port = os.getenv("PORT", 8765)


def setup_logger():
    log_format = "%(asctime)s [%(log_color)s%(levelname)s%(reset)s] %(module)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure the logger to write logs to a file
    file_handler = TimedRotatingFileHandler('app.log', when='midnight', backupCount=7)
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


async def process_message(websocket: WebSocketServerProtocol):
    async for message in websocket:
        try:
            parsed = SocketMessage(**json.loads(message))
            match parsed.message_type:
                case MessageType.NewMessage:
                    message_payload = ChatMessage(**parsed.payload)

                    # Act on message content if desired...
                    print(f"{message_payload.sent_by_username}: {message_payload.content}")

                    new_message = SocketMessage(message_type="new_message", payload=message_payload.model_dump())
                    logging.info(new_message)
                    await websocket.send(new_message.model_dump_json())
                case _:
                    logging.warning(f"Received unknown message type {parsed.message_type} - skipping!")
        except Exception as e:
            logging.error(e)


async def main():
    async with serve(process_message, host, port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
