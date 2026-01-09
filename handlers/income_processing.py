import asyncio
from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from decimal import Decimal
from keyboards.inline import get_actions_kb, ActionsCallbackFactory
from .dialog_states import TransactionStates as ts

# Функция для подготовки текста сообщения
# В будущем имеет смысл сделать ее методом класса Transaction
def format_message(**kwargs):
    "Возвращает шаблон сообщения"
    template = f"""
Поступление:
Сумма: {kwargs.get('amount', '--')}
Категория: {kwargs.get('category', '--')}
Описание: {kwargs.get('description', '--')}
{kwargs.get('step_message'):}
"""
    return template

router = Router()

# Хендлер для коллбэка кнопки "Приход"
@router.callback_query(ActionsCallbackFactory.filter(F.action == "income"))
async def add_income(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_content = format_message(amount=data.get('amount'),
                                     step_message='Введите категорию:'
                                     )
    await callback.message.edit_text(message_content)
    await state.update_data(initial_message_id=callback.message.message_id)
    await callback.answer()
    await state.set_state(ts.category)

@router.message(F.text, ts.category)
async def capture_income_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    data = await state.get_data()
    print(f'{message.message_id} - {message.text}')
    await message.delete()
    print(message.message_id, 'is deleted')
    message_content = format_message(amount=data.get('amount'),
                                    category=data.get('category'),
                                    step_message='Введите описание:'
                                    )
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data.get('initial_message_id'),  # ID предыдущего сообщения
        text=message_content
        )
    await state.set_state(ts.description)


@router.message(F.text, ts.description)
async def capture_income_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    print(f'{message.message_id} - {message.text}')
    await message.delete()
    print(message.message_id, 'is deleted')
    message_content = format_message(amount=data.get('amount'),
                                    category=data.get('category'),
                                    description=data.get('description'),
                                    )
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data.get('initial_message_id'),
        text=message_content
        )
    await state.set_state(ts.finish)