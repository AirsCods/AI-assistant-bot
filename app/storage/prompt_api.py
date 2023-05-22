from cachetools import TTLCache

from models import Prompt
from storage.storage import MongoDBPrompt


class PromptApi:
    def __init__(self, prompt_storage: MongoDBPrompt, cache: TTLCache):
        self.storage: MongoDBPrompt = prompt_storage
        self.cache: TTLCache = cache

    async def create_prompt(self, name: str, description: str, prompt: str, author: str):

        prompt_role = Prompt(name=name,
                             description=description,
                             prompt=prompt,
                             author=author)
        await self.storage.create(prompt_role)
        self.cache[name] = prompt_role

    async def save_all(self, prompts_list: list[Prompt]):
        await self.storage.create_all(prompts_list)

    async def get_prompt(self, name: str) -> Prompt:
        if name in self.cache:
            return self.cache[name]

        prompt = await self.storage.read(name)

        if prompt:
            self.cache[name] = prompt
            return prompt

    async def get_all_prompt(self) -> list[Prompt]:
        len_db = await self.storage.storage.count_documents({})
        if len(self.cache) == len_db:
            all_prompt = self.cache.values()
            return list(all_prompt)

        all_prompt = await self.storage.read_all()
        if all_prompt:
            for prompt in all_prompt:
                self.cache[prompt['name']] = prompt
            return all_prompt

    async def update_prompt(self, role_name: str, type_text: str, new_prompt_text: str):
        if type_text == 'text':
            field = 'prompt'
        else:
            field = 'description'
        await self.storage.update(name=role_name, users_field=field, new_data=new_prompt_text)

    async def update_prompt_text(self, name: str, prompt_text: str) -> None:
        await self.storage.update(name=name, users_field='prompt', new_data=prompt_text)

    async def update_prompt_description(self, name: str, description: str) -> None:
        await self.storage.update(name=name, users_field='description', new_data=description)

    async def delete_prompt(self, name: str):
        if name in self.cache:
            self.cache.pop(name)
        await self.storage.delete(name)

    async def close(self):
        await self.storage.close()
