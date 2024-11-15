from peewee import SqliteDatabase

# Подключение к базе данных
db = SqliteDatabase('film_bot.db')

def init_db():
    db.connect()
