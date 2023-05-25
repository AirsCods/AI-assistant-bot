import os

from aiogram import F, types
from aiogram.enums import ContentType
from bot.loader import bot, dp
from bot.states import BotState
from config import MAX_MESSAGE_LENGTH
from loader import bot_core
from loguru import logger
from pydub import AudioSegment


# Обработка сообщений к GPT
@dp.message(BotState.CHAT, F.text | F.voice | F.audio)
async def chat_dialog_handler(message: types.Message):
    """Обработчик на получение голосового и аудио сообщения."""
    await bot.send_chat_action(chat_id=message.chat.id, action='typing', request_timeout=5)

    question = ''
    if message.content_type == ContentType.VOICE:
        path_file = await download_audio_file(message.voice)
        question = await bot_core.llm.get_speech_to_text(path_file)
    elif message.content_type == ContentType.AUDIO:
        path_file = await download_audio_file(message.audio)
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
        await bot.send_chat_action(chat_id=message.chat.id, action='typing', request_timeout=5)
        text_parts = [answer[i:i + MAX_MESSAGE_LENGTH]
                      for i in range(0, len(answer), MAX_MESSAGE_LENGTH)]
        for part in text_parts:
            await message.answer(part)


async def download_audio_file(audio: types.Audio | types.Voice) -> str:
    file_io = await bot.download(audio)
    # Преобразование BytesIO объекта в AudioSegment объект
    audio_segment = AudioSegment.from_file(file_io)
    # Экспорт аудио файла в формат MP3
    logger.info('Сохраняю данные аудио в файл')
    path_file = f"{os.getcwd()}/tmp/{audio.file_id}.mp3"
    audio_segment.export(path_file, format='mp3')
    file_io.close()
    return path_file
