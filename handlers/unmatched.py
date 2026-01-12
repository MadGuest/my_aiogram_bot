from aiogram import Router
from aiogram.types import (
    Message,
    CallbackQuery,
)

import logging
logger = logging.getLogger(__name__)

# Создайте глобальный эхо-роутер
echo_router = Router()

@echo_router.message()
@echo_router.callback_query()
async def echo_handler(event: Message | CallbackQuery):
    logger.warning(f"Unhandled event: {event}")
    
    if isinstance(event, Message):
        await event.answer("Команда не распознана")
    
    return True  # Останавливаем дальнейшую обработку