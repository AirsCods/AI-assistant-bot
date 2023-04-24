from aiogram.fsm.state import StatesGroup, State


class BotState(StatesGroup):
    ADD_USER = State()
    ROLE = State()
    CHAT = State()
    START = State()
    TALK = State()
    TYPE = State()
    ADD_NAME = State()
    ADD_DESC = State()
    ADD_PROMPT = State()
