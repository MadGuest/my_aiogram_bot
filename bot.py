import asyncio
import logging

# Импорты для создания бота
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Хранилище для данных FSM
from aiogram.fsm.storage.memory import MemoryStorage
# Класс для планирования задач
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Загрузка переменных окружения из .env
from config import BOT_TOKEN, db

from handlers.start_command import router as cmd_start_router
from handlers.add_payment import add_payment_router
from handlers.numeric_input import router as numeric_text_router



# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    
    await db.create_tables()
    # Инстанс бота
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Инстанс диспетчера
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(cmd_start_router)
    dp.include_router(numeric_text_router)
    dp.include_router(add_payment_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



