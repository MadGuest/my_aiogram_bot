create_accounts_table = '''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT DEFAULT 'Основной счет',
                    balance REAL DEFAULT 0,
                    is_default BOOLEAN DEFAULT 1,
                    UNIQUE(user_id, name)
                )
            '''

create_transactions_table = '''
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
            '''

create_categories_table = '''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT CHECK(type IN ('income', 'expense', 'transfer')),
                    is_predefined BOOLEAN DEFAULT 0,
                    emoji TEXT DEFAULT '',
                    UNIQUE(user_id, name, type)
                )
            '''