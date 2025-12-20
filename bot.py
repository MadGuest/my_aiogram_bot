import os
import asyncio
import logging

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command

from handlers.start_command import router as cmd_start_router


logging.basicConfig(level=logging.INFO)

load_dotenv()
tg_token = os.getenv("BOT_TOKEN")

bot = Bot(token=tg_token)

dp = Dispatcher()




async def main():
    dp.include_router(cmd_start_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



