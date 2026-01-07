# config.py
import os
from pathlib import Path
from decouple import config, Csv

# Определяем корневую директорию проекта
BASE_DIR = Path(__file__).resolve().parent

# Загружаем конфигурацию из .env
DATABASE_PATH = config('DATABASE_PATH', default='data/database.db')
BOT_TOKEN = config('BOT_TOKEN')

# Формируем абсолютный путь к БД
# Если путь относительный, делаем его абсолютным относительно BASE_DIR
if not Path(DATABASE_PATH).is_absolute():
    DATABASE_PATH = BASE_DIR / DATABASE_PATH

# Создаем директорию для базы данных, если она не существует
DATABASE_DIR = Path(DATABASE_PATH).parent
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Проверяем обязательные настройки
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в .env файле!")

# Можно добавить вывод в лог для отладки
print(f"[CONFIG] База данных: {DATABASE_PATH}")
print(f"[CONFIG] Директория БД создана: {DATABASE_DIR.exists()}")