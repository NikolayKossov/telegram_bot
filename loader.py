from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from database.core import db
from database.common.models import SearchHistory, Movie

# Функция для подключения к базе данных и создания таблиц
def setup():
    db.connect()
    db.create_tables([SearchHistory, Movie])  # Создаем таблицы после импорта моделей

# Вызов функции setup для инициализации базы данных и таблиц
setup()

# Инициализация состояния памяти для бота и создание экземпляра бота
storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
