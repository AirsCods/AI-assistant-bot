from models import User, Prompt, Message
from storage import HistoryApi, PromptApi


class BotCorePromptMixin:
    def __init__(self, user_storage: HistoryApi, prompt_storage: PromptApi):
        self.user_storage = user_storage
        self.prompt_storage = prompt_storage

    async def get_all_prompt(self):
        return await self.prompt_storage.get_all_prompt()

    async def create_prompt(self, **kwargs):
        await self.prompt_storage.create_prompt(**kwargs)

    async def update_prompt(self, *args):
        await self.prompt_storage.update_prompt(*args)

    async def add_role(self, *args):
        await self.prompt_storage.create_prompt(*args)


class BotCoreMenuCommandsMixin:
    def __init__(self, user_storage: HistoryApi, prompt_storage: PromptApi):
        self.user_storage = user_storage
        self.prompt_storage = prompt_storage

    async def set_outpat_type(self, user_id, outpat_type: str):
        await self.user_storage.set_type_output(user_id, outpat_type)

    async def get_user_info(self, user_id: int) -> str:
        user_data: User = await self.user_storage.get_user_data(user_id)
        bot_role = user_data["bot_role"]
        prompt: Prompt = await self.prompt_storage.get_prompt(bot_role)
        answer = f'-------------------------------------------------------\n' \
                 f'- ID - {user_data["_id"]}\n' \
                 f'- Name - {user_data["name"]}\n' \
                 f'- Role - {bot_role}\n' \
                 f'- Output Type - {user_data["output_type"]}\n' \
                 f'- Bot Prompt -\n{prompt["prompt"]}\n' \
                 f'-------------------------------------------------------'
        return answer

    async def clear_history(self, user_id: int):
        user_data: User = await self.user_storage.get_user_data(user_id)
        history_messages = [user_data['history'][0]]
        await self.user_storage.update_history_messages(user_id, history_messages)

    async def get_history_str(self, user_id: int) -> str:
        user_data: User = await self.user_storage.get_user_data(user_id)
        user_name = user_data['name']
        history_messages_str = f'------ >{user_name}< message history------\n'
        history_messages: list[Message] = user_data['history']

        for item in history_messages:
            role = str(item["role"]).capitalize()
            if role == 'System':
                continue
            content = item["content"]
            history_messages_str += f'>> {role} : {content}\n'

        return history_messages_str[:-1]
