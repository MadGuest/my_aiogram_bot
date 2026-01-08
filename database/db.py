import sqlite3
import aiosqlite
import logging
from typing import Optional
from .queries import create_accounts_table, create_categories_table, create_transactions_table


logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.info(f'Инициализация БД: {db_path}')


    async def create_tables(self):
        try:
            logger.debug(f"Подключение к БД: {self.db_path}")
            async with aiosqlite.connect(self.db_path) as db:
                logger.debug("Подключение к БД установлено")
                await db.execute(create_accounts_table)
                logger.debug("Таблица 'accounts' проверена/создана")
                await db.execute(create_categories_table)
                logger.debug("Таблица 'categories' проверена/создана")
                await db.execute(create_transactions_table)
                await db.commit()
                logger.debug("Таблица 'transactions' проверена/создана")
                logger.info("Таблицы успешно созданы/проверены")
                
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}", exc_info=True)
            raise

