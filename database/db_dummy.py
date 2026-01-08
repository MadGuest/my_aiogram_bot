import sqlite3
import aiosqlite
from typing import Optional

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_tables(self):
        """Создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    username TEXT,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()
            print("Таблицы созданы")

    async def add_user(self, user_id: int, username: str, full_name: str):
        """Добавление пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    'INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
                    (user_id, username, full_name)
                )
                await db.commit()
                return True
            except Exception as e:
                print(f"Ошибка добавления пользователя: {e}")
                return False

    async def get_user(self, user_id: int):
        """Получение пользователя по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT * FROM users WHERE user_id = ?',
                (user_id,)
            )
            user = await cursor.fetchone()
            return user

    async def add_message(self, user_id: int, text: str):
        """Добавление сообщения в историю"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO messages (user_id, text) VALUES (?, ?)',
                (user_id, text)
            )
            await db.commit()

    async def get_user_messages(self, user_id: int, limit: int = 10):
        """Получение последних сообщений пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT * FROM messages WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
                (user_id, limit)
            )
            messages = await cursor.fetchall()
            return messages

    async def get_all_users(self):
        """Получение всех пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM users')
            users = await cursor.fetchall()
            return users

    async def update_username(self, user_id: int, new_username: str):
        """Обновление username пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE users SET username = ? WHERE user_id = ?',
                (new_username, user_id)
            )
            await db.commit()