from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_actions_kb():
    actions_keyboard = [
        [InlineKeyboardButton(text="💰Приход", callback_data='add_income')],
        [InlineKeyboardButton(text="💸Расход", callback_data='add_outcome')],
        [InlineKeyboardButton(text="➡️Перевод", callback_data='add_transfer')],
        [InlineKeyboardButton(text="🧾Платёж", callback_data='add_payment')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=actions_keyboard)