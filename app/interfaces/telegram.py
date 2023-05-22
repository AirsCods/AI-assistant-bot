import asyncio

from aiogram import Bot, Router
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from app.core import BotCore
from bot.utils import on_startup_notify, set_default_commands
from config import BOT_TOKEN


class TelegramInterface:
    def __init__(self, bot_core: BotCore, router: Router):
        self.bot_core = bot_core
        self.router = router

        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher(bot=self.bot, storage=MemoryStorage())
        self.dp.include_router(self.router)

    async def _on_startup(self):
        await self.bot.delete_webhook()
        await on_startup_notify(self.bot)
        await set_default_commands(self.bot)

    async def _start_polling(self):
        try:
            logger.info('------------Telegram bot start polling.------------')
            await self._on_startup()
            await self.dp.start_polling(self.bot, close_bot_session=True)
        except Exception as err:
            logger.error(f'------------:Upper error:------------\n{err}')
        finally:
            logger.info('------------Telegram bot was disabled.------------')

    def start(self):
        asyncio.run(self._start_polling())
        logger.success('Telegram bot was started.')
