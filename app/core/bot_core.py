import datetime
import os

from aiogram.types import FSInputFile
from gtts import gTTS

from bot.states import BotState
from .bot_core_cmd_mixins import BotCorePromptMixin, BotCoreMenuCommandsMixin
from llm.llm_models import LlmAgent
from models import Message, Prompt, RoleType, User
from storage import HistoryApi, PromptApi


class BotCore(BotCorePromptMixin, BotCoreMenuCommandsMixin):
    def __init__(self, user_storage: HistoryApi, prompt_storage: PromptApi, llm: LlmAgent):
        super().__init__(user_storage, prompt_storage)
        self.llm = llm

    async def add_user(self, user_id, user_name, role_name):
        prompt_obj: Prompt = await self.prompt_storage.get_prompt(role_name)
        prompt = prompt_obj['prompt']
        start_message = await self.llm.get_start_message_by_role(prompt)
        user = User(
            _id=user_id,
            name=user_name,
            created_ad=datetime.datetime.utcnow(),
            history=[start_message],
            output_type='text',
            bot_role=role_name,
            state=BotState.CHAT.state
        )
        await self.user_storage.create_user(user)

    async def get_user_data(self, user_id: int) -> User:
        return await self.user_storage.get_user_data(user_id)

    async def set_role(self, user_id: int, role_name: str, ):
        prompt: Prompt = await self.prompt_storage.get_prompt(role_name)
        user_data: User = await self.user_storage.get_user_data(user_id)
        history_messages = user_data['history']
        history_messages[0] = await self.llm.get_start_message_by_role(prompt['prompt'])
        await self.user_storage.update_history_messages(user_id, history_messages)
        await self.user_storage.set_role(user_id, role_name)

    async def get_answer(self, user_id, question):
        """Обработчик на получение голосового и аудио сообщения."""

        user_data: User = await self.user_storage.get_user_data(user_id)

        output_type = user_data['output_type']
        history_messages: list[Message] = user_data['history']

        # Создаю сообщение пользователя и добавляю к истории сообщений
        history_messages.append(Message(role=RoleType.USER.value, content=question))
        history_messages = await self.llm.check_len_history(history_messages)

        # Получаю ответ от ChatGPT
        answer, usage_data = await self.llm.get_chat_response(history_messages)

        # Создаю сообщение ассистента и добавляю в историю сообщений
        history_messages.append(Message(role=RoleType.ASSISTANT.value, content=answer))
        # Сохраняю историю сообщений в БД
        await self.user_storage.update_history_messages(user_id, message_history=history_messages)

        return answer, output_type

    @staticmethod
    async def get_voice_answer(answer: str, user_id: int) -> FSInputFile:
        path_file = f"{os.getcwd()}/tmp/tts_{user_id}"
        tts = gTTS(text=answer, lang="ru", slow=False)
        tts.save(path_file)
        file_voice = FSInputFile(path_file)
        return file_voice
