# database/db.py
import aiosqlite
from typing import Optional, List, Dict, Any, Tuple
from .queries import create_accounts_table, create_transactions_table, create_categories_table
from config import DATABASE_PATH
import logging
import asyncio

logger = logging.getLogger(__name__)

class Database:

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._lock = asyncio.Lock()
    
    async def _get_connection(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    
    async def init_db(self):
        """Инициализация таблиц (выполняется один раз)"""
        async with self._lock:
            if self._initialized:
                return
            
            conn = await self._get_connection()
            try:
                # Таблица счетов
                await conn.execute(create_accounts_table)
                
                # Таблица категорий
                await conn.execute(create_categories_table)
                
                # Таблица транзакций
                await conn.execute(create_transactions_table)
                
                await conn.commit()
                self._initialized = True
                logger.info("Database initialized successfully")
                
            except Exception as e:
                logger.error(f"Database initialization error: {e}")
                raise
            finally:
                await conn.close()
            logger.info("Database initialized successfully")
    
    # ===== ACCOUNTS =====
    async def create_account(self, user_id: int, name: str = "Основной счет", 
                           balance: float = 0, is_default: bool = True) -> int:
        """Создать новый счет"""
        async with await self._get_connection() as conn:
            cursor = await conn.execute('''
                INSERT INTO accounts (user_id, name, balance, is_default)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, balance, is_default))
            await conn.commit()
            return cursor.lastrowid
    
    async def get_accounts(self, user_id: int) -> List[Dict]:
        """Получить все счета пользователя"""
        async with await self._get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM accounts WHERE user_id = ? ORDER BY is_default DESC, id
            ''', (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_default_account(self, user_id: int) -> Optional[Dict]:
        """Получить счет по умолчанию"""
        async with await self._get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM accounts 
                WHERE user_id = ? AND is_default = 1 
                LIMIT 1
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    # ===== CATEGORIES =====
    async def create_category(self, user_id: int, name: str, type: str, 
                            emoji: str = "", is_predefined: bool = False) -> int:
        """Создать категорию"""
        async with await self._get_connection() as conn:
            cursor = await conn.execute('''
                INSERT INTO categories (user_id, name, type, emoji, is_predefined)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, type, emoji, is_predefined))
            await conn.commit()
            return cursor.lastrowid
    
    async def get_categories(self, user_id: int, type: Optional[str] = None) -> List[Dict]:
        """Получить категории пользователя"""
        async with await self._get_connection() as conn:
            query = "SELECT * FROM categories WHERE user_id = ?"
            params = [user_id]
            
            if type:
                query += " AND type = ?"
                params.append(type)
            
            query += " ORDER BY is_predefined DESC, name"
            
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    # ===== TRANSACTIONS =====
    async def create_transaction(self, user_id: int, account_id: int, 
                               amount: float, type: str, 
                               category_id: Optional[int] = None,
                               description: Optional[str] = None) -> int:
        """Создать транзакцию и обновить баланс счета"""
        async with await self._get_connection() as conn:
            # Начинаем транзакцию
            await conn.execute("BEGIN")
            
            try:
                # Создаем запись о транзакции
                cursor = await conn.execute('''
                    INSERT INTO transactions 
                    (user_id, account_id, category_id, amount, type, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, account_id, category_id, amount, type, description))
                transaction_id = cursor.lastrowid
                
                # Обновляем баланс счета
                if type == 'income':
                    await conn.execute('''
                        UPDATE accounts 
                        SET balance = balance + ? 
                        WHERE id = ? AND user_id = ?
                    ''', (amount, account_id, user_id))
                elif type == 'expense':
                    await conn.execute('''
                        UPDATE accounts 
                        SET balance = balance - ? 
                        WHERE id = ? AND user_id = ?
                    ''', (amount, account_id, user_id))
                # Для transfer нужна отдельная логика с двумя счетами
                
                await conn.commit()
                return transaction_id
                
            except Exception as e:
                await conn.rollback()
                logger.error(f"Transaction failed: {e}")
                raise
    
    async def get_transactions(self, user_id: int, limit: int = 10, 
                             offset: int = 0) -> List[Dict]:
        """Получить последние транзакции пользователя"""
        async with await self._get_connection() as conn:
            async with conn.execute('''
                SELECT t.*, a.name as account_name, c.name as category_name
                FROM transactions t
                LEFT JOIN accounts a ON t.account_id = a.id
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                ORDER BY t.date DESC
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_balance(self, user_id: int) -> float:
        """Получить общий баланс пользователя"""
        async with await self._get_connection() as conn:
            async with conn.execute('''
                SELECT SUM(balance) as total_balance 
                FROM accounts 
                WHERE user_id = ?
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row['total_balance'] if row['total_balance'] else 0.0

# Создаем глобальный экземпляр БД
db = Database()