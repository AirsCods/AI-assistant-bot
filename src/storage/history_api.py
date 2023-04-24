import tiktoken
from cachetools import TTLCache
from loguru import logger

from models.types import Message, User
from .storage_interface import StorageInterface


class HistoryApi:
    def __init__(self, user_storage: StorageInterface, cache: TTLCache):
        self.storage: StorageInterface = user_storage
        self.cache: TTLCache = cache

    async def create_user(self, user: User) -> None:
        # Сохраняем данные пользователя в бд и кеш
        await self.storage.create(user)
        self.cache[user['_id']] = user

    async def get_user_data(self, user_id: int) -> User | None:
        if user_id in self.cache:
            return self.cache[user_id]

        logger.info(f'Получаю данные пользователя из базы данных')
        user_data: User = await self.storage.read(user_id)

        if user_data:
            logger.info('Данные получены')
            self.cache[user_id] = user_data
            return user_data

    async def update_history_messages(self, user_id: int, message_history: list[Message]):
        # Обновляем историю сообщений в базе данных
        await self.storage.update(
            user_id=user_id,
            users_field='history',
            new_data=message_history
        )
        # Обновляем историю сообщений в кэше
        if user_id in self.cache:
            self.cache[user_id]['history'] = message_history

    async def set_type_output(self, user_id: int, type_output: str):
        await self.storage.update(
            user_id=user_id,
            users_field='output_type',
            new_data=type_output
        )
        # Обновляем настройки бота в кэше
        if user_id in self.cache:
            self.cache[user_id]['output_type'] = type_output

    async def set_role(self, user_id: int, role_name: str):
        await self.storage.update(
            user_id=user_id,
            users_field='bot_role',
            new_data=role_name
        )
        # Обновляем настройки бота в кэше
        if user_id in self.cache:
            self.cache[user_id]['bot_role'] = role_name

    @staticmethod
    async def story_shortening(history: list[Message], total_tokens: int) -> list[Message]:
        logger.info(f'Total tokens in prompt: {total_tokens}. Clear start of history.')

        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        tokens_removed = 0

        while tokens_removed < 400:
            for i in range(2):
                tokens_removed += len(encoding.encode(history[4]['content']))
                del history[4]
        logger.info(f'Delete {tokens_removed} tokens in history. Total: {total_tokens - tokens_removed}')

        return history

    async def close(self):
        await self.storage.close()
        self.cache.clear()
