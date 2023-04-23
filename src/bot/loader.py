from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from cachetools import TTLCache

from config import OPENAI_CONFIG, BOT_TOKEN, DB_URL_CONNECT
from llm.llm_models import LlmAgent
from storage.history_api import HistoryApi
from storage.storage import MongoDBStorage
from storage.storage_interface import StorageInterface

db_storage: StorageInterface = MongoDBStorage(DB_URL_CONNECT)
user_cache: TTLCache = TTLCache(maxsize=5000, ttl=3600)
user_storage = HistoryApi(user_storage=db_storage, cache=user_cache)

llm = LlmAgent(OPENAI_CONFIG)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
