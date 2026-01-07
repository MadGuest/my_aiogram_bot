# database/__init__.py
from .db import db

async def init_database():
    """Инициализация базы данных при старте"""
    await db.init_db()

# Экспортируем объект БД для использования в других модулях
__all__ = ['db', 'init_database']