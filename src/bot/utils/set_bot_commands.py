from aiogram import types, Bot
from loguru import logger

cmd_start = [
    ('go', 'Запустить бота.'),
]


async def set_default_commands(bot: Bot):
    commands_list = [types.BotCommand(command=cmd, description=desc) for cmd, desc in cmd_start]
    await bot.set_my_commands(commands_list)
    logger.info('Стандартные команды назначены!')
