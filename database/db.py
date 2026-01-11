import sqlite3
import aiosqlite
import logging
import traceback
from functools import wraps
from typing import Optional
from .queries import (create_accounts_table,
                      create_categories_table,
                      create_transactions_table,
                      category_name_unique,
                      category_name_unique_update)
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


def safe_db_method(fallback_value=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"Database error in {func.__name__}: {e}\n{traceback.format_exc()}")
                return fallback_value
        return wrapper
    return decorator

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.info(f'Инициализация БД: {db_path}')

    @asynccontextmanager
    async def _connection(self):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("PRAGMA foreign_keys = ON")
            yield conn
            await conn.commit()


    async def create_tables(self):
        try:
            logger.debug(f"Подключение к БД: {self.db_path}")
            async with self._connection() as conn:
                logger.debug("Подключение к БД установлено")
                await conn.execute(create_accounts_table)
                logger.debug("Таблица 'accounts' проверена/создана")
                await conn.execute(create_categories_table)
                await conn.execute(category_name_unique)
                await conn.execute(category_name_unique_update)
                logger.debug("Таблица 'categories' проверена/создана")
                await conn.execute(create_transactions_table)
                await conn.commit()
                logger.debug("Таблица 'transactions' проверена/создана")
                logger.info("Таблицы успешно созданы/проверены")
                
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}", exc_info=True)
            raise

    async def get_categories_list(self):
        async with self._connection() as conn:
            cursor = await conn.execute('SELECT * FROM categories')
            categories = await cursor.fetchall()
            return categories

    async def get_category_by_id(self, id):
        async with self._connection() as conn:
            cursor = await conn.execute("SELECT name, type FROM categories WHERE id = ?", (id,))
            category = await cursor.fetchone()
            return category
        
    async def get_category_name_by_id(self, id):
        async with self._connection() as conn:
            cursor = await conn.execute("SELECT name FROM categories WHERE id = ?", (id,))
            category = await cursor.fetchone()
            return category
        
    async def delete_category_by_id(self, id):
        async with self._connection() as conn:
            cursor = await conn.execute("DELETE FROM categories WHERE id = ?", (id,))
            return cursor   


    async def add_category(self, name: str, type: str):
        """Добавление категории"""
        async with self._connection() as conn:
            try:
                await conn.execute(
                    'INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)',
                    (name, type)
                )
                await conn.commit()
                return True
            except Exception as e:
                logger.info(f"Ошибка добавления категории: {e}")
                return False
            
    async def update_name(self, id: int, new_name: str):
        """Обновление названия категории"""
        async with  self._connection() as conn:
            try:
                await conn.execute(
                    'UPDATE categories SET name = ? WHERE id = ?',
                    (new_name, id)
                )
                await conn.commit()
                return True
            except Exception as e:
                logger.info(f"Ошибка изменения категории: {e}")
                return False           




