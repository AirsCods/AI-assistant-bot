import datetime
import os
import tempfile

from aiogram import Router, types
from aiogram.enums import ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from gtts import gTTS
from loguru import logger

from bot.keyboards.role import get_role_keyboard, get_type_keyboard
from bot.loader import user_storage, llm
from bot.states import BotState
from models.types import BotRole, Message, RoleType
from models.types import User

router = Router()


@router.message(Command('go_talk'))
@router.message(Command('set_role'), BotState.CHAT)
async def cmd_choose_role(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(BotState.ROLE)
    role_keyboard = get_role_keyboard()
    await message.answer('Выберите роль для ассистента:', reply_markup=role_keyboard)


@router.message(Command('set_output'), BotState.CHAT)
async def cmd_set_output(message: types.Message, state: FSMContext):
    await state.set_state('choose_type')
    await message.delete()
    type_keyboard = get_type_keyboard()
    await message.answer('Выберите формат ответов ассистента:', reply_markup=type_keyboard)


@router.callback_query(StateFilter('choose_type'))
async def choose_type(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    type_output = callback.data
    await user_storage.set_type_output(user_id, type_output)


@router.callback_query(StateFilter(BotState.ROLE))
# @router.callback_query()
async def choose_language(callback: CallbackQuery, state: FSMContext):
    role_name = callback.data
    role = BotRole.__getitem__(role_name)
    user = User(
        _id=callback.from_user.id,
        name=callback.from_user.full_name,
        created_ad=datetime.datetime.utcnow(),
        history=[await llm.get_start_message_by_role(role)],
        bot_config={
            'output_type': 'text',
        }
    )
    await user_storage.create_user(user)
    print('Пользователь сохранен.')

    await callback.answer(
        text=f'Вы выбрали роль ассистента: {callback.data}.',
        show_alert=True
    )
    await callback.message.delete()
    await state.set_state(BotState.CHAT)


@router.message(BotState.CHAT)
async def chat_dialog(message: types.Message):
    """Обработчик на получение голосового и аудио сообщения."""

    user_id = message.from_user.id
    question = message.text
    user_data: User = await user_storage.get_user_data(user_id)
    history_messages: list[Message] = user_data['history']
    print(history_messages)

    if message.content_type == ContentType.VOICE:
        question = await llm.get_text_recognize(message.voice)

    elif message.content_type == ContentType.AUDIO:
        question = await llm.get_text_recognize(message.audio)

    elif message.content_type == ContentType.TEXT:
        question = message.text

    user_message = Message(role=RoleType.USER.value, content=question)
    history_messages.append(user_message)

    # Получаю ответ
    answer, usage_data = await llm.get_chat_response(history_messages)

    # Добавление ответа в историю сообщений
    ai_message = Message(role=RoleType.ASSISTANT.value, content=answer)
    history_messages.append(ai_message)

    # Проверка длинны истории
    if usage_data.total_tokens > 2200:
        history_messages = await user_storage.story_shortening(history_messages, usage_data.total_tokens)

    await user_storage.update_history_messages(user_id, message_history=history_messages)

    if user_data['bot_config']['output_type'] == 'audio':
        # Создаем объект gTTS с указанным текстом и языком
        logger.info('Перевожу текст в аудио')
        tts = gTTS(text=answer, lang="ru", slow=False)
        # Создаем временный файл и сохраняем его имя
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_filename = f.name

        # Сохраняем сгенерированный голосовой файл во временный файл
        tts.save(temp_filename)

        # Открываем временный файл и отправляем его содержимое пользователю в виде голосового сообщения
        with open(temp_filename, "rb") as voice:
            await message.answer_voice(voice)

        # Удаляем временный файл после отправки голосового сообщения
        os.unlink(temp_filename)

    elif user_data['bot_config']['output_type'] == 'text':
        await message.answer(answer)
