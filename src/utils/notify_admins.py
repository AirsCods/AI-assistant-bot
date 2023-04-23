from aiogram import Bot
from loguru import logger

from config import admins


async def on_startup_notify(bot: Bot):
    for admin in admins:
        try:
            await bot.send_message(chat_id=admin, text='Бот запущен!')
        except Exception as err:
            logger.exception(err)

    logger.info('Бот запущен')
