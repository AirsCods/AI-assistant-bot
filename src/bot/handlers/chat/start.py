import datetime

from aiogram import Router, types
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.menu import get_start_menu, get_chat_menu
from bot.keyboards.role import get_role_keyboard
from bot.loader import user_storage, llm
from bot.states import BotState
from models.types import BotRole
from models.types import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.delete()
    answer = f'Добро пожаловать {message.from_user.full_name}! Вас приветствует бот-ассистент.\n' \
             f'Вы можете выбрать роль своего ассистента и настроить текстовый или голосовой формат ответов.\n' \
             f'Для подробной информации введите команду /help.'
    start_menu = get_start_menu()
    await message.answer(answer, reply_markup=start_menu)
    await state.set_state(BotState.START)


@router.message(Command('go_talk'), BotState.START)
async def first_choose_role(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(BotState.ADD_USER)
    role_keyboard = get_role_keyboard()
    await message.answer('Выберите роль для ассистента:', reply_markup=role_keyboard)


@router.callback_query(StateFilter(BotState.ADD_USER))
async def add_user(callback: CallbackQuery, state: FSMContext):
    role_name = callback.data
    role = BotRole.__getitem__(role_name)
    user = User(
        _id=callback.from_user.id,
        name=callback.from_user.full_name,
        created_ad=datetime.datetime.utcnow(),
        history=[await llm.get_start_message_by_role(role)],
        output_type='text',
        bot_role=role_name
    )
    await user_storage.create_user(user)
    await callback.answer(text=f'Вы выбрали роль ассистента: {callback.data}.')
    await state.set_state(BotState.CHAT)
    await callback.message.delete()


@router.message(Command('menu'), BotState.CHAT)
async def cmd_menu(message: types.Message, state: FSMContext):
    await message.delete()
    chat_menu = get_chat_menu()
    await message.answer('Chat menu:', reply_markup=chat_menu)


@router.message(Command('menu'))
async def cmd_menu(message: types.Message, state: FSMContext):
    await message.delete()
    start_menu = get_start_menu()
    await message.answer('Start menu:', reply_markup=start_menu)
    await state.set_state(BotState.START)


@router.message(Command('help'), StateFilter(BotState.CHAT, BotState.START))
async def cmd_help(message: types.Message):
    await message.delete()
    await message.answer(
        'Бот поддерживает следующие команды:\n'
        '/go_talk - Запустить ассистента.\n'
        '/set_role - Выбрать роль бота.\n'
        '/set_output - Выбрать формат ответов.\n'
        '/get_user_info - Показать данные пользователя.\n'
        '/help - Помощь!'
    )
