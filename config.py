# config.py
import os
from pathlib import Path
from decouple import config, Csv
from database.db import Database

import logging
logger = logging.getLogger(__name__)

# Определяем корневую директорию проекта
BASE_DIR = Path(__file__).resolve().parent

# Загружаем конфигурацию из .env
DATABASE_PATH = config('DATABASE_PATH', default='data/dummy.db')
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

db = Database(DATABASE_PATH)
