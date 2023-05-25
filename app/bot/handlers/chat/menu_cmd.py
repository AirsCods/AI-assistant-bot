from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards import get_role_keyboard, get_type_keyboard, get_change_keyboard
from bot.states import BotState
from config import MAX_MESSAGE_LENGTH
from loader import bot_core
from bot.loader import dp


# Установить роль ассистента
@dp.callback_query(StateFilter(BotState.CHAT), Text('set_role'))
async def cmd_set_role(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.ROLE)
    await callback.message.delete()

    prompts = await bot_core.get_all_prompt()
    role_keyboard = get_role_keyboard(prompts)

    await callback.answer()
    await callback.message.answer('Выберите роль для ассистента:', reply_markup=role_keyboard)


@dp.callback_query(StateFilter(BotState.ROLE))
async def callback_set_role(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    role_name = callback.data
    await bot_core.set_role(user_id, role_name)

    await state.set_state(BotState.CHAT)
    await callback.message.delete()
    await callback.answer(text=f'Вы выбрали роль ассистента: {callback.data}.', show_alert=True)


# Установить тип ответа
@dp.callback_query(StateFilter(BotState.CHAT), Text('set_output'))
async def cmd_set_output(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.TYPE)
    await callback.message.delete()

    type_keyboard = get_type_keyboard()
    await callback.answer()
    await callback.message.answer('Выберите формат ответов ассистента:', reply_markup=type_keyboard)


@dp.callback_query(StateFilter(BotState.TYPE))
async def callback_set_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await callback.message.delete()

    user_id = callback.from_user.id
    outpat_type = callback.data
    await bot_core.set_outpat_type(user_id, outpat_type)
    await callback.answer(f'Вы выбрали формат: {outpat_type}.', show_alert=True)


# Получить информацию о пользователе
@dp.callback_query(Text('get_user_info'), StateFilter(BotState.CHAT))
async def cmd_get_info(callback: CallbackQuery):
    await callback.message.delete()
    user_id = callback.from_user.id
    answer = await bot_core.get_user_info(user_id)
    await callback.answer()
    await callback.message.answer(answer)


# Очистить историю сообщений
@dp.callback_query(Text('clear_history'), StateFilter(BotState.CHAT))
async def cdm_clear_history(callback: CallbackQuery):
    await callback.message.delete()
    user_id = callback.from_user.id
    await bot_core.clear_history(user_id)
    await callback.answer('История сообщений ассистента очищена.', show_alert=True)


# Получить историю сообщений
@dp.callback_query(Text('get_history'), StateFilter(BotState.CHAT))
async def cdm_get_history(callback: CallbackQuery):
    await callback.message.delete()
    user_id = callback.from_user.id
    history_messages_str = await bot_core.get_history_str(user_id)

    if len(history_messages_str) > MAX_MESSAGE_LENGTH:
        for chunk in [history_messages_str[i:i + MAX_MESSAGE_LENGTH]
                      for i in range(0, len(history_messages_str), MAX_MESSAGE_LENGTH)]:
            await callback.message.answer(chunk)
    else:
        await callback.message.answer(history_messages_str)


# Обновление текста промпта
@dp.callback_query(StateFilter(BotState.CHAT), Text('update_role'))
async def update_prompt_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.UPDATE_PROMPT)
    await callback.message.delete()

    prompts = await bot_core.get_all_prompt()
    role_keyboard = get_role_keyboard(prompts)

    await callback.answer()
    await callback.message.answer('Выберите роль для изменения', reply_markup=role_keyboard)


@dp.callback_query(StateFilter(BotState.UPDATE_PROMPT))
async def callback_set_role(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHOOSE_UPDATE)
    await callback.message.delete()

    role_name = callback.data
    await state.update_data(name=role_name)
    await callback.answer(text=f'Вы выбрали роль для изменений текста: {role_name}.', show_alert=True)

    change_keyboard = get_change_keyboard()
    await callback.message.answer('Что изменить у роли:', reply_markup=change_keyboard)


@dp.callback_query(StateFilter(BotState.CHOOSE_UPDATE), Text('prompt'))
async def callback_set_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHANGE_TEXT)
    await callback.message.delete()
    await callback.message.answer('Введите новый промпт роли:')


@dp.message(BotState.CHANGE_TEXT)
async def change_prompt(message: types.Message, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await message.delete()

    state_data = await state.get_data()
    role_name = state_data['name']
    new_prompt_text = message.text

    await bot_core.update_prompt(role_name, 'text', new_prompt_text)
    await message.answer('Промпт роли изменен!')


@dp.callback_query(StateFilter(BotState.CHOOSE_UPDATE), Text('description'))
async def callback_set_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.CHANGE_DESC)
    await callback.message.delete()
    await callback.message.answer('Введите новое описание роли:')


@dp.message(BotState.CHANGE_TEXT)
async def change_prompt(message: types.Message, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await message.delete()

    state_data = await state.get_data()
    role_name = state_data['name']
    new_prompt_text = message.text

    await bot_core.update_prompt(role_name, 'desc', new_prompt_text)
    await message.answer('Описание роли изменено!')


# Добавление роли
@dp.callback_query(StateFilter(BotState.CHAT), Text('add_role'))
async def cmd_add_role(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(BotState.ADD_NAME)
    await callback.message.answer('Введите название роли:')


@dp.message(StateFilter(BotState.ADD_NAME))
async def add_name(message: types.Message, state: FSMContext):
    await state.set_state(BotState.ADD_DESC)
    await state.update_data(name=message.text)
    await message.delete()
    await message.answer('Введите описание роли:')


@dp.message(StateFilter(BotState.ADD_DESC))
async def add_description(message: types.Message, state: FSMContext):
    await state.set_state(BotState.ADD_PROMPT)
    await state.update_data(description=message.text)
    await message.delete()
    await message.answer('Введите промпт роли:')


@dp.message(BotState.ADD_PROMPT)
async def add_prompt(message: types.Message, state: FSMContext):
    await state.set_state(BotState.CHAT)
    await state.update_data(prompt=message.text)
    await message.delete()

    data = await state.get_data()
    name = data['name'].upper(),
    description = data['description'],
    prompt = data['prompt'],
    author = message.from_user.full_name

    await bot_core.add_role(name, description, prompt, author)
    await message.answer('Роль добавлена в базу данных.')
