from aiogram import types
from storage import HistoryApi, PromptApi


class BotCoreStartCommandsMixin:
    def __init__(self, user_storage: HistoryApi, prompt_storage: PromptApi):
        self.user_storage = user_storage
        self.prompt_storage = prompt_storage


class BotCoreMenuCommandsMixin:
    def __init__(self, user_storage: HistoryApi, prompt_storage: PromptApi):
        self.user_storage = user_storage
        self.prompt_storage = prompt_storage


class BotCoreChatMixin:
    def __init__(self, user_storage: HistoryApi, prompt_storage: PromptApi):
        self.user_storage = user_storage
        self.prompt_storage = prompt_storage
