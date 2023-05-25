import os

from aiogram import types, F
from aiogram.enums import ContentType
from loguru import logger

from bot.states import BotState
from config import MAX_MESSAGE_LENGTH
from loader import bot_core
from .start import router


# Обработка сообщений к GPT
@router.message(BotState.CHAT, F.text | F.voice | F.audio)
async def chat_dialog_handler(message: types.Message):
    """Обработчик на получение голосового и аудио сообщения."""

    question = ''
    if message.content_type == ContentType.VOICE:
        path_file = await tg_bot.download_audio_file(message.voice)
        question = await bot_core.llm.get_speech_to_text(path_file)
    elif message.content_type == ContentType.AUDIO:
        path_file = await tg_bot.download_audio_file(message.audio)
        question = await bot_core.llm.get_speech_to_text(path_file)
    elif message.content_type == ContentType.TEXT:
        question = message.text

    user_id = message.from_user.id
    answer, output_type = await bot_core.get_answer(user_id, question)

    if output_type == 'voice':
        logger.info('Перевожу текст в аудио')
        file_voice = await bot_core.get_voice_answer(answer, user_id)
        await message.answer_voice(file_voice)
        os.remove(file_voice.path)

    elif output_type == 'text':
        text_parts = [answer[i:i + MAX_MESSAGE_LENGTH]
                      for i in range(0, len(answer), MAX_MESSAGE_LENGTH)]
        for part in text_parts:
            await message.answer(part)
