from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from decimal import Decimal
from keyboards.inline import get_actions_kb, ActionsCallbackFactory

router = Router()

@router.callback_query(ActionsCallbackFactory.filter(F.action == "income"))
async def add_income(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(f"Обработчик для добавления прихода {data.get('amount')}")
    await callback.answer()