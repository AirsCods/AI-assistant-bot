from datetime import datetime
from enum import Enum
from typing import TypedDict


class RoleType(Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'


class Message(TypedDict):
    role: RoleType
    content: str


class User(TypedDict):
    _id: int
    name: str
    history: list[Message]
    output_type: str
    bot_role: str
    created_ad: datetime


class Prompt(TypedDict):
    name: str
    description: str
    prompt: str
    author: str
