from aiogram import Router, types
from aiogram.filters import Command

from aiogram.utils.keyboard import InlineKeyboardBuilder

builder1 = InlineKeyboardBuilder()
builder1.button(text="Кнопка 1", callback_data="btn1")
builder1.button(text="Кнопка 2", callback_data="btn2")
builder1.adjust(2)

builder2 = InlineKeyboardBuilder()
builder2.button(text="Кнопка 3", callback_data="btn3")
builder2.button(text="Кнопка 4", callback_data="btn4")
builder2.adjust(2)

# Объединяем: сначала builder1, потом builder2
builder1.attach(builder2)
keyboard = builder1.as_markup()

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!!!", reply_markup=keyboard)

