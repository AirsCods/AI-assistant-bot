from aiogram import types
from aiogram.filters import CommandStart, StateFilter, Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards import get_role_keyboard, get_chat_menu
from bot.loader import dp
from bot.states import BotState
from loader import bot_core
from models import User


# Команда старт. Запуск бота.
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(BotState.ADD_USER)
    await message.delete()

    answer = f'Добро пожаловать {message.from_user.full_name}! Вас приветствует бот-ассистент.\n' \
             f'Выберите роль для ассистента:\n'

    prompts = await bot_core.get_all_prompt()

    role_keyboard = get_role_keyboard(prompts)
    await message.answer(answer, reply_markup=role_keyboard)


# Добавление пользователя или обновление.
@dp.callback_query(StateFilter(BotState.ADD_USER))
async def add_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await callback.message.delete()
    role_name = callback.data
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name

    await bot_core.add_user(user_id, user_name, role_name)

    await callback.answer(text=f'Ассистент в роли {role_name} готов к диалогу!🎱', show_alert=True)
    await callback.message.answer(f'Ассистент в роли {role_name} готов к диалогу!🎱')


# Команда открытия меню
@dp.message(Command('menu'), BotState.CHAT)
async def cmd_go_chat(message: types.Message):
    await message.delete()
    chat_menu = get_chat_menu()
    await message.answer('Cписок команд:', reply_markup=chat_menu)


# Команда открытия меню
@dp.message(Command('go'))
async def cmd_go_all(message: types.Message, state: FSMContext):
    await message.delete()
    user_id = message.from_user.id
    user_data: User = await bot_core.user_storage.get_user_data(user_id)

    if user_data:
        role_name = user_data['bot_role']
        await state.set_state(BotState.CHAT)
        await message.answer(f'C возращением {message.from_user.username}.\n'
                             f'Вы общаетесь с {role_name}.')

    else:
        await message.answer(f'Мы с вами не знакомы {message.from_user.first_name}\n'
                             f' Для регистрации нажмите команду /start.')


@dp.callback_query(Text('help'), StateFilter(BotState.CHAT))
@dp.callback_query(Command('help'), StateFilter(BotState.CHAT))
async def cmd_help(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer(
        'Бот поддерживает следующие команды:\n'
        '/menu - Открыть меню.\n'
        '/help - Помощь!'
    )
