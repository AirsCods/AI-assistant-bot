from typing import Optional

import tiktoken
from cachetools import TTLCache
from loguru import logger

from models.types import Message, User
from storage.interface import StorageInterface


class HistoryApi:
    def __init__(self, user_storage: StorageInterface, cache: TTLCache):
        self.storage: StorageInterface = user_storage
        self.cache: TTLCache = cache

    async def create_user(self, user: User) -> None:
        user_id = user['_id']
        try:
            result = await self.storage.read(user_id)
        except Exception as e:
            logger.error(f"Error reading user data from database: {e}")
            return

        if result is None:
            logger.info(f'User {user["name"]} save to MongoDB')
            await self.storage.create(user)
        else:
            logger.info(f'User {user["name"]} exist and update to MongoDB')
            update_data = {
                'name': user['name'],
                'history': user['history'],
                'output_type': user['output_type'],
                'bot_role': user['bot_role']
            }
            await self.storage.update_many(user_id, update_data)

        self.cache[user['_id']] = user

    async def get_user_data(self, user_id: int) -> Optional[User]:
        if user_id in self.cache:
            return self.cache[user_id]

        logger.info(f'Получаю данные пользователя из базы данных')
        try:
            user_data: User = await self.storage.read(user_id)
        except Exception as e:
            logger.error(f"Error reading user data from database: {e}")
            return None

        if user_data:
            self.cache[user_id] = user_data
            return user_data

    async def update_history_messages(self, user_id: int, message_history: list[Message]):
        await self.storage.update(
            user_id=user_id,
            users_field='history',
            new_data=message_history
        )
        if user_id in self.cache:
            self.cache[user_id]['history'] = message_history

    async def set_type_output(self, user_id: int, type_output: str):
        await self.storage.update(
            user_id=user_id,
            users_field='output_type',
            new_data=type_output
        )
        if user_id in self.cache:
            self.cache[user_id]['output_type'] = type_output

    async def set_role(self, user_id: int, role_name: str):
        await self.storage.update(
            user_id=user_id,
            users_field='bot_role',
            new_data=role_name
        )
        if user_id in self.cache:
            self.cache[user_id]['bot_role'] = role_name

    @staticmethod
    async def story_shortening(history: list[Message], usage_data, model: str) -> list[Message]:
        total_tokens = usage_data['total_tokens']

        encoding = tiktoken.encoding_for_model(model)
        tokens_removed = 0

        # while tokens_removed < answer_tokens:
        while (total_tokens - tokens_removed) > 4000:
            tokens_removed += len(encoding.encode(history[3]['content']))
            tokens_removed += len(encoding.encode(history[4]['content']))
            del history[3]
            del history[4]

        return history

    async def close(self):
        await self.storage.close()
        self.cache.clear()
