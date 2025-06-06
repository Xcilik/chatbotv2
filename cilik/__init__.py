import os
import logging
import asyncio
import sys

from pyrogram import Client
from config import *
from pyromod import listen

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
    ],
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.session").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)


class Bot(Client):
    __module__ = "pyrogram.client"
    _bot = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def start(self):
        await super().start()
        self._bot.append(self)
        LOGGER("Info").info(f"Starting Client ({self.me.id}|{self.me.first_name})")


bot = Client(
    name="chat",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)
