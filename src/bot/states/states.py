from aiogram.fsm.state import StatesGroup, State


class BotState(StatesGroup):
    ROLE = State()
    CHAT = State()
    START = State()
    TALK = State()
