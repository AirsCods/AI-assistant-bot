import subprocess

from aiogram import types
from aiogram.filters import Command, StateFilter
from loguru import logger

from bot.loader import dp
from bot.states import BotState
from config import admins, SCRIPT_PATH


@dp.message(StateFilter(BotState.CHAT), Command('update'))
async def cmd_help(message: types.Message):
    logger.info(f'Start cmd UPDATE from user: {message.from_user.username} : {message.from_user.id}')
    if message.from_user.id not in admins:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    process = subprocess.Popen(["bash", SCRIPT_PATH], stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        await message.answer(f"Ошибка при выполнении скрипта: {error}")
    else:
        await message.answer(f"Скрипт успешно выполнен: {output}")
