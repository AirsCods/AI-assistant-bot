import os
import tempfile
from typing import Optional

from aiogram import types
from aiogram.enums import ContentType
from aiogram.types import FSInputFile
from gtts import gTTS
from loguru import logger
from pydub import AudioSegment

from bot.loader import llm, bot


async def get_text_question(message: types.Message) -> str:
    question = ''
    if message.content_type == ContentType.VOICE:
        path_file = await _download_audio_file(message.voice)
        question = await llm.get_speech_to_text(path_file)
    elif message.content_type == ContentType.AUDIO:
        path_file = await _download_audio_file(message.audio)
        question = await llm.get_speech_to_text(path_file)
    elif message.content_type == ContentType.TEXT:
        question = message.text
    return question


async def get_voice_answer(answer: str, user_id: int) -> FSInputFile:
    path_file = f"{os.getcwd()}/tmp/tts_{user_id}"
    logger.info(f'Перевожу текст в аудио {user_id}')
    tts = gTTS(text=answer, lang="ru", slow=False)
    # Сохраняем сгенерированный голосовой файл во временный файл
    tts.save(path_file)
    # Открываем временный файл и отправляем его содержимое пользователю в виде голосового сообщения
    file_voice = FSInputFile(path_file)
    return file_voice


async def get_voice_answer_tempfile(answer: str, user_id: int) -> FSInputFile:
    logger.info(f'Перевожу текст в аудио {user_id}')
    tts = gTTS(text=answer, lang="ru", slow=False)
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp_filename = temp.name
        tts.save(temp.name)
        file_voice = FSInputFile(temp.name)
    print(temp_filename)
    os.unlink(temp_filename)
    return file_voice


async def _download_audio_file(audio: types.Audio | types.Voice) -> str:
    file_io = await bot.download(audio)
    # Преобразование BytesIO объекта в AudioSegment объект
    audio_segment = AudioSegment.from_file(file_io)
    # Экспорт аудио файла в формат MP3
    logger.info('Сохраняю данные аудио в файл')
    path_file = f"{os.getcwd()}/tmp/{audio.file_id}.mp3"
    audio_segment.export(path_file, format='mp3')
    file_io.close()
    return path_file
