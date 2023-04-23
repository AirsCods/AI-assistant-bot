from aiogram.utils.keyboard import InlineKeyboardBuilder

from models.types import BotRole


def get_role_keyboard():
    choose_role_keyboard = InlineKeyboardBuilder()
    for role in BotRole:
        choose_role_keyboard.button(
            text=role.name,
            callback_data=role.name
        )
    choose_role_keyboard.adjust(2)

    return choose_role_keyboard.as_markup()


def get_type_keyboard():
    choose_type_keyboard = InlineKeyboardBuilder()
    choose_type_keyboard.button(
        text='Текст',
        callback_data='text'
    )
    choose_type_keyboard.button(
        text='Голосовые',
        callback_data='voice'
    )

    choose_type_keyboard.adjust(2)

    return choose_type_keyboard.as_markup()
