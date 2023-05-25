import pickle
from typing import Any

from loguru import logger
from models import Prompt, User
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
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

    async def update_many(self, user_id: int, update_data: dict[User.keys, str]) -> None:
        pass

    async def delete(self, user_id: int) -> None:
        self.storage.pop(user_id)

    async def close(self) -> None:
        if self.storage is not None:
            with open(self.file_path, 'wb') as file:
                pickle.dump(self.storage, file)


class MongoDBUser(StorageInterface):
    def __init__(self, url_connect: str):
        super().__init__()
        self._db_client: AsyncIOMotorClient = AsyncIOMotorClient(url_connect)
        self.storage = self._db_client.ai_assistant_db.users

    async def create(self, user: User) -> None:
        await self.storage.insert_one(user)

    async def read(self, user_id: int) -> User | None:
        return await self.storage.find_one({'_id': user_id})

    async def update(self, user_id: int, users_field: User.keys, new_data: Any) -> None:
        await self.storage.update_one({'_id': user_id}, {'$set': {users_field: new_data}})

    async def update_many(self, user_id: int, update_data: dict[User.keys, str]) -> None:
        await self.storage.storage.update_one({'_id': user_id}, {'$set': update_data})

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
