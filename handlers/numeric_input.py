from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State
from aiogram.types import Message
from decimal import Decimal
# from filters.numeric_input_filter import PositiveNumberFilter, NegativeNumberFilter
from filters.numeric_input_filter import NumberFilter
router = Router()

@router.message(F.text, StateFilter(None),NumberFilter())
async def numeric_input_handler(message: Message, number: Decimal):
    await message.delete()
    await message.answer(f"['Приход', 'Расход', 'Перевод', 'Платеж']")







