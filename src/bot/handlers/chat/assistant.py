import os

from aiogram import types, F
from loguru import logger

from bot.loader import user_storage, llm
from bot.states import BotState
from bot.utils import get_text_question, get_voice_answer
from models.types import Message, RoleType, User
from .start import router


# Обработка сообщений к GPT
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

    # Check len
    history_messages = await llm.check_len_history(history_messages)

    # Получаю ответ от ChatGPT
    answer, usage_data = await llm.get_chat_response(history_messages)

    # Создаю сообщение ассистента и добавляю в историю сообщений
    ai_message = Message(role=RoleType.ASSISTANT.value, content=answer)
    history_messages.append(ai_message)
    logger.info('Check len new history')

    model = llm.get_model()
    if '3.5' in model:
        max_token = 2200
    elif '4' in model:
        max_token = 7200
    else:
        max_token = 2000
    # Проверка длинны истории
    if usage_data.total_tokens >= max_token:
        history_messages = await user_storage.story_shortening(history_messages, usage_data, model)

    # Сохраняю историю сообщений в БД
    await user_storage.update_history_messages(user_id, message_history=history_messages)

    if output_type == 'voice':
        file_voice = await get_voice_answer(answer, user_id)
        logger.info('Перевожу текст в аудио')
        await message.answer_voice(file_voice)
        os.remove(file_voice.path)

    elif user_data['output_type'] == 'text':
        MAX_MESSAGE_LENGTH = 4096

        if len(answer) > MAX_MESSAGE_LENGTH:
            for chunk in [answer[i:i + MAX_MESSAGE_LENGTH]
                          for i in range(0, len(answer), MAX_MESSAGE_LENGTH)]:
                await message.answer(chunk)
        else:
            await message.answer(answer)
