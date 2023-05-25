import asyncio

from aiogram import Bot, Dispatcher
from aiogram import types
from loguru import logger

from config import admins


class TelegramInterface:

    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp

    def start(self):
        asyncio.run(self.start_bot())

    async def start_bot(self):
        try:
            logger.info('------------Telegram bot start polling.------------')
            await self.bot.delete_webhook()
            await self._on_startup_notify()
            await self._set_default_commands()

            await self.dp.start_polling(self.bot, close_bot_session=True)

        except Exception as err:
            logger.error(f'------------:Upper error:------------\n{err}')
        finally:
            logger.info('------------Telegram bot was disabled.------------')

    async def _on_startup_notify(self):
        for admin in admins:
            try:
                await self.bot.send_message(chat_id=admin, text='Bot started.')
            except Exception as err:
                logger.exception(err)
        logger.info('Launch notifications sent.')

    async def _set_default_commands(self):
        cmd_start = [
            ('go', 'Запустить бота.'),
            ('menu', 'Меню бота.'),
        ]
        commands_list = [types.BotCommand(command=cmd, description=desc)
                         for cmd, desc in cmd_start]
        await self.bot.set_my_commands(commands_list)
        logger.info('Menu commands assigned.')
