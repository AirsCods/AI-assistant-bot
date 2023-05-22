import os

from aiogram import types
from loguru import logger
from pydub import AudioSegment


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
