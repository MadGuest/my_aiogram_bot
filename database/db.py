import sqlite3 as sq
from aiosqlite import connect as aio_connect
from config import DATABASE_PATH
from .queries import (create_accounts_table,
                     create_categories_table,
                     create_transactions_table)


def db_start():
    # Using synchronous connect for simple, non-async startup task
    with sq.connect(DATABASE_PATH) as base:
        cur = base.cursor()
        if base:
            print('Connect to database successful')
        # Create a "users" table if it doesn't exist
        base.execute(create_accounts_table)
        base.execute(create_categories_table)
        base.execute(create_transactions_table)
        base.commit()



async def main():
    db_start() # Initialize the database tables


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

