import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender


# Состояния для добавления платежа
class Payment(StatesGroup):
    name = State()
    category = State()
    amount = State()
    due_date = State()


add_payment_router = Router()


@add_payment_router.message(Command("add_payment"))
async def add_payment_handler(message: types.Message, state: FSMContext):
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer("Название платежа:")
    await state.set_state(Payment.name)


@add_payment_router.message(F.text, Payment.name)
async def capture_payment_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer("Категория платежа:")
    await state.set_state(Payment.category)


@add_payment_router.message(F.text, Payment.category)
async def capture_payment_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer("Сумма:")
    await state.set_state(Payment.amount)


@add_payment_router.message(F.text, Payment.amount)
async def capture_payment_amount(message: types.Message, state: FSMContext):
    await state.update_data(amount=message.text)
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer("Дата платежа:")
    await state.set_state(Payment.due_date)


@add_payment_router.message(F.text, Payment.due_date)
async def capture_payment_due_date(message: types.Message, state: FSMContext):
    await state.update_data(due_date=message.text)
    data = await state.get_data()
    await message.answer(f"Добавлен платеж:\n"
                         f"{data.get('name')}\n"
                         f"{data.get('category')}\n"
                         f"{data.get('amount')}\n"
                         f"{data.get('due_date')}"
                         )
    await state.clear()
