from aiogram import types, Bot
from loguru import logger


async def set_default_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand(command='go_talk', description='Запустить ассистента.'),
        types.BotCommand(command='set_role', description='Выбрать роль бота.'),
        types.BotCommand(command='set_output', description='Выбрать формат ответов.'),
        types.BotCommand(command='get_user_info', description='Показать данные пользователя.'),
        types.BotCommand(command='get_history', description='Показать историю сообщений бота.'),
        types.BotCommand(command='clear_history', description='Очистить историю сообщений бота.'),
        types.BotCommand(command='help', description='Дополнительная информация!'),
    ])
    logger.info('Стандартные команды назначены!')
