# database.py
import sqlite3
from decouple import config



def init_db():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    
    # Таблица счетов (минимально)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT DEFAULT 'Основной счет',
            balance REAL DEFAULT 0,
            is_default BOOLEAN DEFAULT 1
        )
    ''')
    
    # Таблица категорий (предопределенные + пользовательские)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense', 'transfer')),
            is_predefined BOOLEAN DEFAULT 0,
            emoji TEXT DEFAULT ''
        )
    ''')
    
    # Таблица транзакций (ядро)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            category_id INTEGER,
            amount REAL NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense', 'transfer')),
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    conn.commit()
    conn.close()