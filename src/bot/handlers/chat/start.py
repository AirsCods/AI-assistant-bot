import datetime

from aiogram import Router, types
from aiogram.filters import StateFilter, CommandStart, Text, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards import get_chat_menu, get_role_keyboard
from bot.loader import user_storage, llm, prompt_storage
from bot.states import BotState
from models.types import User, Prompt

router = Router()


# Команда старт. Запуск бота.
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(BotState.ADD_USER)
    await message.delete()

    answer = f'Добро пожаловать {message.from_user.full_name}! Вас приветствует бот-ассистент.\n' \
             f'Выберите роль для ассистента:\n'
    prompts = await prompt_storage.get_all_prompt()

    role_keyboard = get_role_keyboard(prompts)
    await message.answer(answer, reply_markup=role_keyboard)


# Добавление пользователя или обновление.
@router.callback_query(StateFilter(BotState.ADD_USER))
async def add_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await callback.message.delete()
    role_name = callback.data
    prompt_obj: Prompt = await prompt_storage.get_prompt(role_name)
    prompt = prompt_obj['prompt']
    start_message = await llm.get_start_message_by_role(prompt)

    user = User(
        _id=callback.from_user.id,
        name=callback.from_user.full_name,
        created_ad=datetime.datetime.utcnow(),
        history=[start_message],
        output_type='text',
        bot_role=role_name,
        state=BotState.CHAT.state
    )

    await user_storage.create_user(user)
    await callback.answer(text=f'Ассистент в роли {role_name} готов к диалогу!🎱', show_alert=True)
    await callback.message.answer(f'Ассистент в роли {role_name} готов к диалогу!🎱')


# Команда открытия меню
@router.message(Command('go'), BotState.CHAT)
async def cmd_go_chat(message: types.Message):
    await message.delete()
    chat_menu = get_chat_menu()
    await message.answer('Cписок команд:', reply_markup=chat_menu)


# Команда открытия меню
@router.message(Command('go'))
async def cmd_go_all(message: types.Message, state: FSMContext):
    await message.delete()
    user_id = message.from_user.id
    user_data: User = await user_storage.get_user_data(user_id)
    if user_data:
        role_name = user_data['bot_role']
        await state.set_state(BotState.CHAT)
        await message.answer(f'C возращением {message.from_user.username}.\n'
                             f'Вы общаетесь с {role_name}.')
    else:
        await message.answer(f'Мы с вами не знакомы {message.from_user.first_name}\n'
                             f' Для регистрации нажмите команду /start.')


@router.callback_query(Text('help'), StateFilter(BotState.CHAT))
async def cmd_help(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer(
        'Бот поддерживает следующие команды:\n'
        '/go - Открыть меню.\n'
        '/help - Помощь!'
    )
