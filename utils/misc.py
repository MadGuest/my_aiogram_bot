from typing import Optional, Union
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

async def handle_message_or_callback(
    event: Union[Message, CallbackQuery],
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    delete_command: bool = False
):
    """Универсальная обработка Message и CallbackQuery"""
    if isinstance(event, Message):
        if delete_command:
            await event.delete()
        await event.answer(text, reply_markup=reply_markup)
    else:
        await event.message.edit_text(text, reply_markup=reply_markup)
        await event.answer()