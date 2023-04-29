from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards import get_role_keyboard, get_type_keyboard, get_change_keyboard
from bot.loader import user_storage, llm, prompt_storage
from bot.states import BotState
from models.types import Message, User, Prompt
from .start import router


# Установить роль ассистента
@router.callback_query(StateFilter(BotState.CHAT), Text('set_role'))
async def cmd_set_role(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.ROLE)
    await callback.message.delete()

    prompts = await prompt_storage.get_all_prompt()
    print(prompts)
    role_keyboard = get_role_keyboard(prompts)

    await callback.answer()
    await callback.message.answer('Выберите роль для ассистента:', reply_markup=role_keyboard)


@router.callback_query(StateFilter(BotState.ROLE))
async def callback_set_role(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await callback.message.delete()

    role_name = callback.data
    prompt: Prompt = await prompt_storage.get_prompt(role_name)

    user_id = callback.from_user.id
    user_data: User = await user_storage.get_user_data(user_id)
    history_messages = user_data['history']
    history_messages[0] = await llm.get_start_message_by_role(prompt['prompt'])

    await user_storage.update_history_messages(user_id, history_messages)
    await user_storage.set_role(user_id, role_name)

    await callback.answer(text=f'Вы выбрали роль ассистента: {callback.data}.', show_alert=True)


# Установить тип ответа
@router.callback_query(StateFilter(BotState.CHAT), Text('set_output'))
async def cmd_set_output(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.TYPE)
    await callback.message.delete()

    type_keyboard = get_type_keyboard()
    await callback.answer()
    await callback.message.answer('Выберите формат ответов ассистента:', reply_markup=type_keyboard)


@router.callback_query(StateFilter(BotState.TYPE))
async def callback_set_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await callback.message.delete()

    user_id = callback.from_user.id
    type_output = callback.data

    await user_storage.set_type_output(user_id, type_output)
    await callback.answer(f'Вы выбрали формат: {type_output}.', show_alert=True)


# Получить информацию о пользователе
@router.callback_query(Text('get_user_info'), StateFilter(BotState.CHAT))
async def cmd_get_info(callback: CallbackQuery):
    await callback.message.delete()

    user_id = callback.from_user.id
    user_data: User = await user_storage.get_user_data(user_id)
    bot_role = user_data["bot_role"]

    prompt: Prompt = await prompt_storage.get_prompt(bot_role)
    answer = f'-------------------------------------------------------\n' \
             f'- ID - {user_data["_id"]}\n' \
             f'- Name - {user_data["name"]}\n' \
             f'- Role - {bot_role}\n' \
             f'- Output Type - {user_data["output_type"]}\n' \
             f'- Bot Prompt -\n{prompt["prompt"]}\n' \
             f'-------------------------------------------------------'

    await callback.answer()
    await callback.message.answer(answer)


# Очистить историю сообщений
@router.callback_query(Text('clear_history'), StateFilter(BotState.CHAT))
async def cdm_clear_history(callback: CallbackQuery):
    await callback.message.delete()

    user_id = callback.from_user.id
    user_data: User = await user_storage.get_user_data(user_id)
    history_messages = [user_data['history'][0]]

    await user_storage.update_history_messages(user_id, history_messages)
    await callback.answer('История сообщений ассистента очищена.', show_alert=True)


# Получить историю сообщений
@router.callback_query(Text('get_history'), StateFilter(BotState.CHAT))
async def cdm_get_history(callback: CallbackQuery):
    await callback.message.delete()
    user_id = callback.from_user.id
    user_data: User = await user_storage.get_user_data(user_id)

    history_messages_str = f'------ >{callback.from_user.username}< message history------\n'
    history_messages: list[Message] = user_data['history']
    for item in history_messages:
        role = str(item["role"]).capitalize()
        if role == 'System':
            continue
        content = item["content"]
        history_messages_str += f'>> {role} : {content}\n'

    history_messages_str = history_messages_str[:-1]
    MAX_MESSAGE_LENGTH = 4096

    if len(history_messages_str) > MAX_MESSAGE_LENGTH:
        for chunk in [history_messages_str[i:i + MAX_MESSAGE_LENGTH]
                      for i in range(0, len(history_messages_str), MAX_MESSAGE_LENGTH)]:
            await callback.message.answer(chunk)
    else:
        await callback.message.answer(history_messages_str)


# Обновление текста промпта
@router.callback_query(StateFilter(BotState.CHAT), Text('update_role'))
async def update_prompt_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.UPDATE_PROMPT)
    await callback.message.delete()

    prompts = await prompt_storage.get_all_prompt()
    role_keyboard = get_role_keyboard(prompts)

    await callback.answer()
    await callback.message.answer('Выберите роль для изменения', reply_markup=role_keyboard)


@router.callback_query(StateFilter(BotState.UPDATE_PROMPT))
async def callback_set_role(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHOOSE_UPDATE)
    await callback.message.delete()

    role_name = callback.data
    await state.update_data(name=role_name)
    await callback.answer(text=f'Вы выбрали роль для изменений текста: {role_name}.', show_alert=True)

    change_keyboard = get_change_keyboard()
    await callback.message.answer('Что изменить у роли:', reply_markup=change_keyboard)


@router.callback_query(StateFilter(BotState.CHOOSE_UPDATE), Text('prompt'))
async def callback_set_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHANGE_TEXT)
    await callback.message.delete()
    await callback.message.answer('Введите новый промпт роли:')


@router.message(BotState.CHANGE_TEXT)
async def change_prompt(message: types.Message, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await message.delete()

    state_data = await state.get_data()
    role_name = state_data['name']
    new_prompt_text = message.text

    await prompt_storage.update_prompt_text(name=role_name, prompt_text=new_prompt_text)
    await message.answer('Промпт роли изменен!')


@router.callback_query(StateFilter(BotState.CHOOSE_UPDATE), Text('description'))
async def callback_set_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHANGE_DESC)
    await callback.message.delete()
    await callback.message.answer('Введите новое описание роли:')


@router.message(BotState.CHANGE_TEXT)
async def change_prompt(message: types.Message, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await message.delete()

    state_data = await state.get_data()
    role_name = state_data['name']
    new_prompt_desc = message.text

    await prompt_storage.update_prompt_description(name=role_name, description=new_prompt_desc)
    await message.answer('Описание роли изменено!')


# Добавление роли
@router.callback_query(StateFilter(BotState.CHAT), Text('add_role'))
async def cmd_add_role(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(BotState.ADD_NAME)
    await callback.message.answer('Введите название роли:')


@router.message(StateFilter(BotState.ADD_NAME))
async def add_name(message: types.Message, state: FSMContext):
    await state.set_state(BotState.ADD_DESC)
    await state.update_data(name=message.text)
    await message.delete()
    await message.answer('Введите описание роли:')


@router.message(StateFilter(BotState.ADD_DESC))
async def add_description(message: types.Message, state: FSMContext):
    await state.set_state(BotState.ADD_PROMPT)
    await state.update_data(description=message.text)
    await message.delete()
    await message.answer('Введите промпт роли:')


@router.message(BotState.ADD_PROMPT)
async def add_prompt(message: types.Message, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await state.update_data(prompt=message.text)
    await message.delete()
    data = await state.get_data()

    await prompt_storage.create_prompt(
        name=data['name'].upper(),
        description=data['description'],
        prompt=data['prompt'],
        author=message.from_user.full_name
    )
    await message.answer('Роль добавлена в базу данных.')
