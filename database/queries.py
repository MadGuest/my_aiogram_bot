create_accounts_table = '''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT DEFAULT 'Основной счет',
                    balance REAL DEFAULT 0,
                    is_default BOOLEAN DEFAULT 1,
                    UNIQUE(name)
                )
            '''

create_transactions_table = '''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    name TEXT NOT NULL,
                    type TEXT CHECK(type IN ('income', 'expense')),
                    emoji TEXT DEFAULT '',
                    UNIQUE(name, type)
                )
            '''

category_name_unique = '''
                CREATE TRIGGER IF NOT EXISTS ensure_category_name_unique
                BEFORE INSERT ON categories
                BEGIN
                    SELECT RAISE(ABORT, 'Category name already exists with any type')
                    WHERE EXISTS (
                        SELECT 1 FROM categories 
                        WHERE name = NEW.name
                        LIMIT 1
                    );
                END;
        '''

category_name_unique_update = '''
            CREATE TRIGGER IF NOT EXISTS ensure_category_name_unique_update
            BEFORE UPDATE ON categories
            BEGIN
                SELECT RAISE(ABORT, 'Category name already exists with any type')
                WHERE EXISTS (
                    SELECT 1 FROM categories 
                    WHERE name = NEW.name 
                    AND id != NEW.id
                    LIMIT 1
                );
            END;
        '''