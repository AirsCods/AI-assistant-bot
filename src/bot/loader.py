from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from cachetools import TTLCache

from config import OPENAI_CONFIG, BOT_TOKEN, DB_URL_CONNECT
from llm.llm_models import LlmAgent
from storage.history_api import HistoryApi
from storage.interface import StorageInterface
from storage.prompt_api import PromptApi
from storage.storage import MongoDBStorage, MongoDBPrompt

db_storage: StorageInterface = MongoDBStorage(DB_URL_CONNECT)
user_cache: TTLCache = TTLCache(maxsize=5000, ttl=3600)
user_storage = HistoryApi(user_storage=db_storage, cache=user_cache)
db_prompt = MongoDBPrompt(DB_URL_CONNECT)
prompt_storage = PromptApi(prompt_storage=db_prompt)

llm = LlmAgent(OPENAI_CONFIG)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
