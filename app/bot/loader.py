import os

from aiogram import Bot, Router, types
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger
from pydub import AudioSegment

from bot.utils import on_startup_notify, set_default_commands
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


class TelegramBot:
    def __init__(self, bot: Bot, router: Router):
        self.bot = bot
        self.dp = Dispatcher(bot=self.bot, storage=MemoryStorage())
        self.dp.include_router(router)

    async def _on_startup(self):
        await self.bot.delete_webhook()
        await on_startup_notify(self.bot)
        await set_default_commands(self.bot)

    async def start_bot(self):
        try:
            logger.info('------------Telegram bot start polling.------------')
            await self._on_startup()
            await self.dp.start_polling(close_bot_session=True)
        except Exception as err:
            logger.error(f'------------:Upper error:------------\n{err}')
        finally:
            logger.info('------------Telegram bot was disabled.------------')

    async def download_audio_file(self, audio: types.Audio | types.Voice) -> str:
        file_io = await self.bot.download(audio)
        # Преобразование BytesIO объекта в AudioSegment объект
        audio_segment = AudioSegment.from_file(file_io)
        # Экспорт аудио файла в формат MP3
        logger.info('Сохраняю данные аудио в файл')
        path_file = f"{os.getcwd()}/tmp/{audio.file_id}.mp3"
        audio_segment.export(path_file, format='mp3')
        file_io.close()
        return path_file
