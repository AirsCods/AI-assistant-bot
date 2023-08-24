import tiktoken
from loguru import logger
from models.types import Message

from .openai_llm import OpenAI


class LlmAgent:
    def __init__(self, openai_config: dict):
        self.open_ai = OpenAI(config=openai_config)

    async def get_speech_to_text(self, audio) -> str:
        return await self.open_ai.get_speech_to_text(audio)

    async def get_start_message_by_role(self, prompt: str) -> Message:
        return await self.open_ai.get_start_message_by_role(prompt)

    async def get_chat_response(self, messages: list[Message]):
        return await self.open_ai.get_chat_answer(messages)

    def get_model(self) -> str:
        return self.open_ai.model

    async def check_len_history(self, history: list[Message]) -> list[Message]:
        encoding = tiktoken.encoding_for_model(self.open_ai.model)
        all_len = 0
        for message in history:
            all_len += len(encoding.encode(message['content']))

        if all_len > self.open_ai.max_len:
            logger.info('Shorting history')
            while all_len > self.open_ai.max_len - 1000:
                all_len -= len(encoding.encode(history[3]['content']))
                del history[3]

        return history
