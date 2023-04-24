import pickle
from typing import Any

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from models.types import User, Prompt
from storage.interface import StorageInterface


class DictStorage(StorageInterface):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.storage: dict
        try:
            with open(self.file_path, 'rb') as file:
                self.storage = pickle.load(file)
        except FileNotFoundError:
            logger.info('Создаю словарь хранилище')
            self.storage = {}

    async def create(self, user: User) -> None:
        user_id = user['_id']
        self.storage[user_id] = user
        await self.close()

    async def read(self, user_id: int) -> User | None:
        return self.storage.get(user_id)

    async def update(self, user_id: int, users_field: User.keys, new_data: Any) -> None:
        self.storage[user_id][users_field] = new_data
        await self.close()

    async def delete(self, user_id: int) -> None:
        self.storage.pop(user_id)

    async def close(self) -> None:
        if self.storage is not None:
            with open(self.file_path, 'wb') as file:
                logger.info(f'Записываю в файл.')
                # json.dump(self.storage, file, ensure_ascii=False, indent=4, default=self._serialize_dates)
                pickle.dump(self.storage, file)


class MongoDBStorage(StorageInterface):
    def __init__(self, url_connect: str):
        super().__init__()
        self._db_client: AsyncIOMotorClient = AsyncIOMotorClient(url_connect)
        self.storage = self._db_client.ai_assistant_db.users

    async def create(self, user: User) -> None:
        user_id = user['_id']
        result = await self.storage.find_one(user_id)

        if result is None:
            logger.info(f'User {user["name"]} save to MongoDB')
            await self.storage.insert_one(user)

        else:
            logger.info(f'User {user["name"]} exist and update to MongoDB')
            self.storage.update_one({'_id': user_id},
                                    {'$set': {
                                        'name': user['name'],
                                        'history': user['history'],
                                        'output_type': user['output_type'],
                                        'bot_role': user['bot_role']
                                    }})

    async def read(self, user_id: int) -> User | None:
        return await self.storage.find_one({'_id': user_id})

    async def update(self,
                     user_id: int,
                     users_field: User.keys,
                     new_data: Any) -> None:
        await self.storage.update_one({'_id': user_id}, {'$set': {users_field: new_data}})

    async def delete(self, user_id: int) -> None:
        await self.storage.delete_one({'_id': user_id})

    async def close(self) -> None:
        self._db_client.close()


class MongoDBPrompt(StorageInterface):
    def __init__(self, url_connect: str):
        super().__init__()
        self._db_client: AsyncIOMotorClient = AsyncIOMotorClient(url_connect)
        self.storage: AsyncIOMotorCollection = self._db_client.ai_prompt.prompts

    async def create(self, prompt: Prompt) -> None:
        await self.storage.insert_one(prompt)

    async def create_all(self, prompts_list: list[Prompt]):
        await self.storage.insert_many(prompts_list)

    async def read(self, name: str) -> Prompt | None:
        return await self.storage.find_one({'name': name})

    async def read_all(self) -> list[Prompt]:
        length = await self.storage.count_documents({})
        prompts = await self.storage.find({}).to_list(length=length)
        return prompts

    async def update(self,
                     name: str,
                     users_field: Prompt.keys,
                     new_data: Any) -> None:
        await self.storage.update_one({'name': name}, {'$set': {users_field: new_data}})

    async def delete(self, name: str) -> None:
        await self.storage.delete_one({'_id': name})

    async def close(self) -> None:
        self._db_client.close()
