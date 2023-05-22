from loguru import logger

from app.core import BotCore


class WebInterface:
    def __init__(self, bot_core: BotCore):
        self.bot_core = bot_core

    async def _on_startup(self):
        pass

    def start(self):
        logger.success('Web bot was started.')
        self._on_startup()
