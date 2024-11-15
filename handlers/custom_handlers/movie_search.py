from telegram_bot_pagination import InlineKeyboardPaginator
from telebot.types import InlineKeyboardButton
from api.utils import search_id, search_film
from loader import bot
from peewee import IntegrityError
from database.utilts.db_utils import save_search, save_movie  # Импорт функций для сохранения данных

user_data = {}


# Команда для начала процесса поиска фильма
@bot.message_handler(commands=['movie_search'])
def movie_search(message):
    bot.send_message(message.chat.id, "Введите название фильма:")
    bot.register_next_step_handler(message, process_name_step)


# Обрабатываем шаг с вводом названия фильма
def process_name_step(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'name': message.text}  # Сохраняем название фильма
    save_search(user_id=chat_id, query=message.text)  # Сохраняем запрос пользователя в историю
    bot.send_message(chat_id, "Введите жанры фильма через запятую (можно оставить пустым для всех жанров):")
    bot.register_next_step_handler(message, process_genre_step)


# Обрабатываем шаг с вводом жанра фильма
def process_genre_step(message):
    chat_id = message.chat.id
    genres_input = message.text.strip()
    genres = [genre.strip() for genre in
              genres_input.split(',')] if genres_input else None  # Преобразуем жанры в список
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

    # Делаем запрос к API Кинопоиска
    movies_id = search_id.search_movie_by_name(name, 10)  # Запрашиваем всегда 10 фильмов
    movies_data = []

    for movie_id in movies_id:
        movie_film = search_film.get_movie_by_id(movie_id, genres)
        if movie_film:  # Проверяем, что фильм найден
            movies_data.append(movie_film)

    # Ограничиваем фильмы до указанного лимита
    user_data[chat_id]['movies_data'] = movies_data[:limit]
    send_movie_page(message, chat_id, 1)


# Функция для отправки информации о фильме и отображения пагинации
def send_movie_page(message, chat_id, page=1):
    movies_data = user_data[chat_id]['movies_data']
    total_pages = len(movies_data)  # Количество фильмов равно количеству страниц
    movie = movies_data[page - 1]  # Получаем текущий фильм

    movie_info = (
        f"Название: {movie['name']}\n"
        f"Описание: {movie.get('description', 'Описание отсутствует')}\n"
        f"Жанры: {', '.join([genre['name'] for genre in movie['genres']])}\n"
        f"Год: {movie.get('year', 'Год не указан')}\n"
        f"Возрастной рейтинг: {movie.get('ageRating', 'Не указан')}\n"
        f"Рейтинг: {movie.get('rating', {}).get('kp', 'Рейтинг не указан')}\n"
        f"Постер: {movie['poster'].get('url', 'Постер отсутствует')}\n"
    )

    # Сохраняем фильм в базу данных после вывода пользователю
    save_movie_to_db(movie)

    # Создаем пагинацию для навигации между фильмами
    paginator = InlineKeyboardPaginator(
        total_pages,
        current_page=page,
        data_pattern='movie#{page}'
    )

    # Проверяем, нужна ли кнопка "Назад"
    if page > 1:
        paginator.add_before(
            InlineKeyboardButton('⬅️ Назад', callback_data=f'movie#{page - 1}')
        )

    # Проверяем, нужна ли кнопка "Вперед"
    if page < total_pages:
        paginator.add_after(
            InlineKeyboardButton('➡️ Вперед', callback_data=f'movie#{page + 1}')
        )

    # Отправляем сообщение с информацией о фильме и клавиатурой для навигации
    bot.send_message(
        message.chat.id,
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
    bot.delete_message(chat_id, call.message.message_id)  # Удаляем предыдущее сообщение
    send_movie_page(call.message, chat_id, page)
