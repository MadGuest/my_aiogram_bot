from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Optional

class ActionsCallbackFactory(CallbackData, prefix="act"):
    action: str
    value: Optional[int] = None

def get_actions_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="💰Приход", callback_data=ActionsCallbackFactory(action="income"))
    builder.button(text="💸Расход", callback_data=ActionsCallbackFactory(action="outcome"))
    builder.button(text="➡️Перевод", callback_data=ActionsCallbackFactory(action="transfer"))
    builder.button(text="🧾Платёж", callback_data=ActionsCallbackFactory(action="payment"))
    builder.adjust(1)
    return builder.as_markup()