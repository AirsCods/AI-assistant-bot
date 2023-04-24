from llm.openai_llm import OpenAI
from models.types import Message


class LlmAgent:
    def __init__(self, openai_config: dict):
        self.open_ai = OpenAI(config=openai_config)

    async def start_agent(self):
        await self.open_ai.start()

    async def get_speech_to_text(self, audio) -> str:
        return await self.open_ai.get_speech_to_text(audio)

    async def get_start_message_by_role(self, description: str) -> Message:
        return await self.open_ai.get_start_message_by_role(description)

    async def get_chat_response(self, messages: list[Message]):
        return await self.open_ai.get_chat_answer(messages)
