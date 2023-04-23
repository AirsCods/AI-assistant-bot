from aiogram import types, F
from aiogram.filters import Command

from bot.loader import router


@router.message(Command(commands=['start']))
async def cmd_start_handler(message: types.Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@router.message(F.text)
async def echo_handler(message: types.Message) -> None:
    await message.answer(message.text + 'ЛАЛАЛА')
