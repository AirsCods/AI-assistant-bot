from aiogram.utils.keyboard import InlineKeyboardBuilder

cmd_chat = [
    ('add_role', 'Добавить роль бота.'),
    ('set_role', 'Выбрать роль бота.'),
    ('set_output', 'Выбрать формат ответов.'),
    ('get_user_info', 'Показать данные пользователя.'),
    ('get_history', 'Показать историю сообщений бота.'),
    ('clear_history', 'Очистить историю сообщений бота.'),
    ('help', 'Дополнительная информация!'),
]

cmd_start = [
    ('go_talk', 'Запустить ассистента.'),
]


def get_start_menu():
    start_menu = InlineKeyboardBuilder()
    for cmd, description in cmd_start:
        start_menu.button(
            text=f'{cmd}',
            callback_data=f'cmd_{cmd}'
        )
    start_menu.adjust(3)
    menu_as_markup = start_menu.as_markup()
    menu_as_markup.resize_keyboard = True
    menu_as_markup.one_time_keyboard = True
    menu_as_markup.input_field_placeholder = 'Нажмите на команду.'
    return menu_as_markup


def get_chat_menu():
    start_menu = InlineKeyboardBuilder()
    for cmd, description in cmd_chat:
        start_menu.button(
            text=f'{cmd}',
            callback_data=f'{cmd}'
        )
    start_menu.adjust(2)
    menu_as_markup = start_menu.as_markup()
    menu_as_markup.resize_keyboard = True
    menu_as_markup.one_time_keyboard = True
    menu_as_markup.input_field_placeholder = 'Нажмите на команду.'
    menu_as_markup.selective = True
    menu_as_markup.is_persistent = True
    return menu_as_markup
