from aiogram import types, Bot
from loguru import logger


async def set_default_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand(command='go_talk', description='Запустить бота.'),
        types.BotCommand(command='set_role', description='Изменить роль бота.'),
        types.BotCommand(command='set_output', description='Выбрать формат ответов.'),
        types.BotCommand(command='get_user_info', description='Показать данные пользователя.'),
    ])
    logger.info('Стандартные команды назначены!')
