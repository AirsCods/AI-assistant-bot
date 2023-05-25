import asyncio

from aiogram import Bot
from loguru import logger

from bot.loader import TelegramBot, bot
from config import BOT_TOKEN


class TelegramInterface:
    def __init__(self, bot):
        self.bot = TelegramBot(bot=bot)


    def start(self):
        asyncio.run(self.bot.start_bot())
        logger.success('Telegram bot was started.')
