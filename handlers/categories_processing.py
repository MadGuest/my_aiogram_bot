from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("categories"))
async def cmd_categories(message: types.Message):
    await message.answer("Hello!!!")