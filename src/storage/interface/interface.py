from typing import Any

from models.types import User


class StorageInterface:
    """Interface for any storage message history"""

    def __init__(self):
        self.storage = None

    async def create(self, user: User) -> None:
        raise NotImplementedError

    async def read(self, user_id: int) -> User | None:
        raise NotImplementedError

    async def update(self, user_id: int, users_field: User.keys, new_data: Any) -> None:
        raise NotImplementedError

    async def update_many(self, user_id: int, update_data: dict[User.keys, str]) -> None:
        raise NotImplementedError

    async def delete(self, user_id: int) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError
