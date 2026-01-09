from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from decimal import Decimal
# from filters.numeric_input_filter import PositiveNumberFilter, NegativeNumberFilter
from filters.numeric_input_filter import NumberFilter
from keyboards.inline import get_actions_kb, ActionsCallbackFactory


router = Router()

# Когда пользователь вводит сумму (любое число) бот показывает клавиатуру с действиями
# Приход/Расход/Перевод
@router.message(F.text, StateFilter(None),NumberFilter())
async def numeric_input_handler(message: Message, number: Decimal, state: FSMContext):
    amount =number
    await state.update_data(amount=amount)  # Сохраняем сумму
    await message.delete()
    await message.answer(f"Добавить операцию на сумму: {number}", reply_markup=get_actions_kb())




@router.callback_query(ActionsCallbackFactory.filter(F.action == "outcome"))
async def add_outcome(callback: CallbackQuery):
    await callback.message.edit_text("Обработчик для добавления расхода")
    await callback.answer()

@router.callback_query(ActionsCallbackFactory.filter(F.action == "transfer"))
async def add_transfer(callback: CallbackQuery):
    await callback.message.edit_text("Обработчик для добавления перевода")
    await callback.answer()

@router.callback_query(ActionsCallbackFactory.filter(F.action == "payment"))
async def menu_payment(callback: CallbackQuery):
    await callback.message.edit_text("Обработчик для добавления платежа")
    await callback.answer()






