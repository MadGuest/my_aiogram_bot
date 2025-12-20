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
        bot_answer = await message.answer("Название платежа:")
        await state.update_data(prev_message_id=bot_answer.message_id)
    await state.set_state(Payment.name)


@add_payment_router.message(F.text, Payment.name)
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

    
    # if prev_message_id := data.get("prev_message_id"):
    #     try:
    #         await message.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id)
    #     except Exception:
    #         pass
    # async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
    #     await asyncio.sleep(2)
    #     bot_answer = await message.answer("Категория платежа:")
    #     await state.update_data(prev_message_id=bot_answer.message_id)
    await state.set_state(Payment.category)


@add_payment_router.message(F.text, Payment.category)
async def capture_payment_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    data = await state.get_data()
    if prev_message_id := data.get("prev_message_id"):
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id)
        except Exception:
            pass
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        bot_answer = await message.answer("Сумма:")
        await state.update_data(prev_message_id=bot_answer.message_id)
    await state.set_state(Payment.amount)


@add_payment_router.message(F.text, Payment.amount)
async def capture_payment_amount(message: types.Message, state: FSMContext):
    await state.update_data(amount=message.text)
    data = await state.get_data()
    if prev_message_id := data.get("prev_message_id"):
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id)
        except Exception:
            pass
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        bot_answer = await message.answer("Дата платежа:")
        await state.update_data(prev_message_id=bot_answer.message_id)
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
