from telegram_bot_pagination import InlineKeyboardPaginator
from api.utils.search_high_budget_movie import get_high_budget_movies  # Импортируем функцию для получения фильмов
from loader import bot
from peewee import IntegrityError
from database.utilts.db_utils import save_search, save_movie  # Импорт функций для сохранения данных

user_data = {}

# Команда для поиска фильмов с высоким бюджетом
@bot.message_handler(commands=['high_budget_movie'])
def high_budget_movie_search(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}  # Инициализируем данные для этого чата
    bot.send_message(chat_id, "Введите название фильма:")
    bot.register_next_step_handler(message, process_name_step)

# Обрабатываем шаг с вводом названия фильма
def process_name_step(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text  # Сохраняем название фильма
    save_search(user_id=chat_id, query=message.text)  # Сохраняем запрос пользователя в историю
    bot.send_message(chat_id, "Введите жанры фильма через запятую (можно оставить пустым для всех жанров):")
    bot.register_next_step_handler(message, process_genre_step)

# Обрабатываем шаг с вводом жанра фильма
def process_genre_step(message):
    chat_id = message.chat.id
    genres_input = message.text.strip()
    genres = [genre.strip() for genre in genres_input.split(',')] if genres_input else None  # Преобразуем жанры в список
    user_data[chat_id]['genres'] = genres  # Сохраняем жанры фильма
    bot.send_message(chat_id, "Введите количество фильмов для вывода (по умолчанию 10):")
    bot.register_next_step_handler(message, process_limit_step)

# Обрабатываем шаг с вводом лимита
def process_limit_step(message):
    chat_id = message.chat.id
    try:
        limit = int(message.text)  # Проверяем, является ли введенное значение числом
    except ValueError:
        limit = 10  # Если пользователь не ввел число, по умолчанию 10

    user_data[chat_id]['limit'] = limit  # Сохраняем лимит

    # Получаем все данные
    name = user_data[chat_id]['name']
    genres = user_data[chat_id]['genres']
    limit = user_data[chat_id]['limit']

    # Делаем запрос к API для фильмов с высоким бюджетом
    movies_data = get_high_budget_movies(name, limit=10, genres=genres)  # Запрашиваем 10 фильмов для сортировки

    if not movies_data:
        bot.send_message(chat_id, "Фильмы не найдены.")
        return

    # Ограничиваем фильмы до указанного лимита
    user_data[chat_id]['movies_data'] = movies_data[:limit]
    user_data[chat_id]['current_page'] = 1
    send_movie_page(chat_id)

# Функция для отправки информации о фильме и отображения пагинации
def send_movie_page(chat_id):
    if chat_id not in user_data or 'movies_data' not in user_data[chat_id] or not user_data[chat_id]['movies_data']:
        bot.send_message(chat_id, "Извините, данные о фильмах отсутствуют. Попробуйте начать новый поиск.")
        return

    page = user_data[chat_id]['current_page']
    movies_data = user_data[chat_id]['movies_data']
    total_pages = len(movies_data)
    movie = movies_data[page - 1]

    movie_info = (
        f"Название: {movie['name']}\n"
        f"Описание: {movie.get('description', 'Описание отсутствует')}\n"
        f"Бюджет: {movie.get('budget', {}).get('value', 'Не указан')} {movie.get('budget', {}).get('currency', '')}\n"
        f"Жанры: {', '.join([genre['name'] for genre in movie['genres']])}\n"
        f"Год: {movie.get('year', 'Год не указан')}\n"
        f"Возрастной рейтинг: {movie.get('ageRating', 'Не указан')}\n"
        f"Рейтинг: {movie.get('rating', {}).get('kp', 'Рейтинг не указан')}\n"
        f"Постер: {movie['poster'].get('url', 'Постер отсутствует')}\n"
    )

    # Сохраняем фильм в базу данных после вывода пользователю
    save_movie_to_db(movie)

    paginator = InlineKeyboardPaginator(
        total_pages,
        current_page=page,
        data_pattern='movie#{page}'
    )

    bot.send_message(
        chat_id,
        movie_info,
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )

# Функция для сохранения фильма в базу данных
def save_movie_to_db(movie):
    try:
        save_movie(
            title=movie['name'],
            description=movie.get('description', 'Описание отсутствует'),
            rating=movie.get('rating', {}).get('kp', 0.0),
            year=movie.get('year', 0),
            genre=', '.join([genre['name'] for genre in movie['genres']]),
            age_rating=movie.get('ageRating', 'Не указан'),
            poster_url=movie['poster'].get('url', 'Постер отсутствует')
        )
        print(f"Фильм '{movie['name']}' сохранен в базе данных.")
    except IntegrityError:
        print(f"Фильм '{movie['name']}' уже существует в базе данных.")

# Обработчик для переключения между страницами фильмов
@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'movie')
def movie_page_callback(call):
    page = int(call.data.split('#')[1])
    chat_id = call.message.chat.id
    if chat_id not in user_data or 'movies_data' not in user_data[chat_id]:
        bot.send_message(chat_id, "Извините, данные о фильмах отсутствуют. Попробуйте начать новый поиск.")
        return

    user_data[chat_id]['current_page'] = page
    bot.delete_message(chat_id, call.message.message_id)  # Удаляем предыдущее сообщение
    send_movie_page(chat_id)
