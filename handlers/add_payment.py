# Обработчик диалога добавления платежа

import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender
from utils.single_message_dialog import SingleMessageDialog


# Состояния для добавления платежа
class Payment(StatesGroup):
    name = State()
    category = State()
    amount = State()
    due_date = State()
    finish = State()


add_payment_router = Router()

smd = SingleMessageDialog()

@add_payment_router.message(Command("add_payment"))
async def add_payment_handler(message: types.Message, state: FSMContext):
    await smd.initial_message(message, state, text="Название:")
    await state.set_state(Payment.name)

@add_payment_router.message(Payment.name)
async def capture_payment_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data.get("prev_message_id"),
        text= "Категория платежа:"
    )
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id
                                     )


    await state.update_data(name=message.text)
    await smd.next_step(message, state, text="Категория:")
    await state.set_state(Payment.category)   

@add_payment_router.message(Payment.category)
async def capture_payment_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await smd.next_step(message, state, text="Сумма:")
    await state.set_state(Payment.amount)   


@add_payment_router.message(Payment.amount)
async def capture_payment_amount(message: types.Message, state: FSMContext):
    await state.update_data(amount=message.text)
    await smd.next_step(message, state, text="Дата платежа:")
    await state.set_state(Payment.due_date)


@add_payment_router.message(Payment.due_date)
async def capture_payment_due_date(message: types.Message, state: FSMContext):
    await state.update_data(due_date=message.text)
    data = await state.get_data()
    answer = (f"Добавлен платеж:\n"
                         f"{data.get('name')}\n"
                         f"{data.get('category')}\n"
                         f"{data.get('amount')}\n"
                         f"{data.get('due_date')}"
                         )
    await smd.last_step(message, state, answer)
    await asyncio.sleep(0.1)
    await state.set_state(None)
    