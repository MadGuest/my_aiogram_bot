from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State
from aiogram.types import Message
from decimal import Decimal
# from filters.numeric_input_filter import PositiveNumberFilter, NegativeNumberFilter
from filters.numeric_input_filter import NumberFilter
from keyboards.inline import get_actions_kb
router = Router()

@router.message(F.text, StateFilter(None),NumberFilter())
async def numeric_input_handler(message: Message, number: Decimal):
    await message.delete()
    await message.answer("Добавить операцию", reply_markup=get_actions_kb())







