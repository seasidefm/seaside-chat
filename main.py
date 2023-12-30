import asyncio
import os
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from websockets.server import serve
from colorlog import ColoredFormatter
from dotenv import load_dotenv

from services.chat import ChatService

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


chat = ChatService()


async def main():
    async with serve(chat.process_message, host, port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
