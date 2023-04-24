from models.types import Prompt
from storage.storage import MongoDBPrompt


class PromptApi:
    def __init__(self, prompt_storage: MongoDBPrompt):
        self.storage: MongoDBPrompt = prompt_storage
        self.prompts: list[Prompt]

    async def create_prompt(self, name: str, description: str, prompt: str, author: str):
        prompt = Prompt(name=name,
                        description=description,
                        prompt=prompt,
                        author=author)
        await self.storage.create(prompt)

    async def save_all(self, prompts_list: list[Prompt]):
        await self.storage.create_all(prompts_list)

    async def get_prompt(self, name: str) -> Prompt:
        return await self.storage.read(name)

    async def get_all_prompt(self):
        return await self.storage.read_all()

    async def delete_prompt(self, name: str):
        await self.storage.delete(name)

    async def close(self):
        await self.storage.close()
