import os

from aiogram import types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.keyboards import get_role_keyboard, get_type_keyboard
from bot.loader import user_storage, llm
from bot.states import BotState
from models.types import BotRole, Message, RoleType, User
from utils.checkers import get_text_question, get_voice_answer
from .start import router


@router.message(Command('set_role'), BotState.CHAT)
async def cmd_set_role(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(BotState.ROLE)
    role_keyboard = get_role_keyboard()
    await message.answer('Выберите роль для ассистента:', reply_markup=role_keyboard)


@router.callback_query(StateFilter(BotState.ROLE))
async def callback_set_role(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    role_name = callback.data
    role = BotRole.__getitem__(role_name)
    new_history = [await llm.get_start_message_by_role(role)]
    await user_storage.set_role(user_id, role_name)
    await user_storage.update_history_messages(user_id, new_history)
    await callback.answer(text=f'Вы выбрали роль ассистента: {callback.data}.')
    await state.set_state(BotState.CHAT)
    await callback.message.delete()


@router.message(Command('set_output'), BotState.CHAT)
async def cmd_set_output(message: types.Message, state: FSMContext):
    type_keyboard = get_type_keyboard()
    await message.answer('Выберите формат ответов ассистента:', reply_markup=type_keyboard)
    await message.delete()
    await state.set_state(BotState.TYPE)


@router.callback_query(StateFilter(BotState.TYPE))
async def callback_set_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHAT)
    user_id = callback.from_user.id
    type_output = callback.data
    await user_storage.set_type_output(user_id, type_output)
    await callback.answer()
    await callback.message.delete()


@router.message(Command('get_user_info'), BotState.CHAT)
async def cmd_get_info(message: types.Message):
    await message.delete()
    user_id = message.from_user.id
    user_data: User = await user_storage.get_user_data(user_id)
    bot_role = user_data["bot_role"]
    role = BotRole.__getitem__(bot_role)
    answer = f'-------------------------------------------------------\n' \
             f'- ID - {user_data["_id"]}\n' \
             f'- Name - {user_data["name"]}\n' \
             f'- Role - {bot_role}\n' \
             f'- Output Type - {user_data["output_type"]}\n' \
             f'- Bot Prompt -\n{role.value}\n' \
             f'-------------------------------------------------------'
    await message.answer(answer)


@router.message(BotState.CHAT, F.text | F.voice | F.audio)
async def chat_dialog_handler(message: types.Message):
    """Обработчик на получение голосового и аудио сообщения."""
    question = await get_text_question(message)
    user_id = message.from_user.id
    user_data: User = await user_storage.get_user_data(user_id)
    output_type = user_data['output_type']
    history_messages: list[Message] = user_data['history']

    # Создаю сообщение пользователя и добавляю к истории сообщений
    user_message = Message(role=RoleType.USER.value, content=question)
    history_messages.append(user_message)

    # Получаю ответ от ChatGPT
    answer, usage_data = await llm.get_chat_response(history_messages)

    # Создаю сообщение ассистента и добавляю в историю сообщений
    ai_message = Message(role=RoleType.ASSISTANT.value, content=answer)
    history_messages.append(ai_message)

    # Проверка длинны истории
    if usage_data.total_tokens > 2200:
        history_messages = await user_storage.story_shortening(history_messages, usage_data.total_tokens)

    # Сохраняю историю сообщений в БД
    await user_storage.update_history_messages(user_id, message_history=history_messages)

    if output_type == 'voice':
        file_voice = await get_voice_answer(answer, user_id)
        logger.info('Перевожу текст в аудио')
        await message.answer_voice(file_voice)
        os.remove(file_voice.path)

    elif user_data['output_type'] == 'text':
        await message.answer(answer)
