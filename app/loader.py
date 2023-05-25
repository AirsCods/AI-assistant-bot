from cachetools import TTLCache
from config import DB_URL_CONNECT, OPENAI_CONFIG
from core import BotCore
from storage import PromptApi
from storage.history_api import HistoryApi
from storage.interface import StorageInterface
from storage.storage import MongoDBPrompt, MongoDBUser

from app.llm.llm_models import LlmAgent

# инициализация хранилища пользователей
db_storage: StorageInterface = MongoDBUser(DB_URL_CONNECT)
user_cache: TTLCache = TTLCache(maxsize=5000, ttl=3600)
user_storage = HistoryApi(user_storage=db_storage, cache=user_cache)

# инициализация хранилища промптов
db_prompt = MongoDBPrompt(DB_URL_CONNECT)
prompt_cache: TTLCache = TTLCache(maxsize=1000, ttl=3600)
prompt_storage = PromptApi(prompt_storage=db_prompt, cache=prompt_cache)

# инициализация ии
llm = LlmAgent(OPENAI_CONFIG)

# инициализация ядра
bot_core = BotCore(user_storage, prompt_storage, llm)
