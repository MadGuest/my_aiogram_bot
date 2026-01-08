from aiogram import Router, types
from aiogram.filters import Command
from database.db_dummy import Database
from config import db

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Добавляем пользователя в БД
    await db.add_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    
    await message.answer(
        f"Привет, {user.full_name}!\n"
        f"Твой ID: {user.id}\n\n"
        "Доступные команды:\n"
        "/profile - твой профиль\n"
        "/stats - статистика\n"
        "/mylast - последние сообщения"
    )

@router.message(Command("profile"))
async def cmd_profile(message: types.Message):
    """Просмотр профиля"""
    user_data = await db.get_user(message.from_user.id)
    
    if user_data:
        # user_data - это кортеж: (id, user_id, username, full_name, created_at)
        await message.answer(
            f"📋 Твой профиль:\n"
            f"ID: {user_data[1]}\n"
            f"Username: @{user_data[2] or 'нет'}\n"
            f"Имя: {user_data[3]}\n"
            f"Зарегистрирован: {user_data[4]}"
        )
    else:
        await message.answer("Профиль не найден. Напиши /start")

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Статистика бота"""
    users = await db.get_all_users()
    await message.answer(f"👥 Всего пользователей в боте: {len(users)}")

@router.message(Command("mylast"))
async def cmd_mylast(message: types.Message):
    """Последние сообщения пользователя"""
    messages = await db.get_user_messages(message.from_user.id, limit=5)
    
    if not messages:
        await message.answer("У тебя еще нет сохраненных сообщений")
        return
    
    text = "📝 Твои последние сообщения:\n\n"
    for msg in messages:
        # msg: (id, user_id, text, created_at)
        text += f"• {msg[2][:50]}...\n"
        text += f"  📅 {msg[3]}\n\n"
    
    await message.answer(text)

@router.message()
async def save_message(message: types.Message):
    """Сохранение всех сообщений пользователя"""
    if message.text:
        await db.add_message(message.from_user.id, message.text)
    
    # Просто эхо для демонстрации
    await message.answer(f"Сообщение сохранено: {message.text[:50]}...")