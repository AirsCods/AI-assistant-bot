from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    CHAT = State()
    START = State()
    TALK = State()
    TYPE = State()

    ADD_USER = State()
    ROLE = State()

    ADD_NAME = State()
    ADD_DESC = State()
    ADD_PROMPT = State()

    UPDATE_PROMPT = State()
    CHOOSE_UPDATE = State()
    CHANGE_TEXT = State()
    CHANGE_DESC = State()
