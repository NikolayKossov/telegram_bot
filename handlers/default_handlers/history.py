from loader import bot
from database.common.models import SearchHistory, Movie
from telegram_bot_pagination import InlineKeyboardPaginator
from telebot.types import InlineKeyboardButton


# Команда для вывода истории поиска
@bot.message_handler(commands=['history'])
def get_search_history(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Получаем историю поиска для пользователя
    history_records = SearchHistory.select().where(SearchHistory.user_id == user_id).order_by(SearchHistory.date.desc())

    if history_records.exists():
        movie_data = []
        for record in history_records:
            # Извлекаем все фильмы, содержащие текст запроса
            movies = Movie.select().where(Movie.title.contains(record.query))
            for movie in movies:
                # Добавляем информацию о фильме и дате поиска
                movie_data.append({
                    'movie': movie,
                    'date': record.date  # Добавляем дату запроса
                })

        # Если найдены фильмы, выводим первый фильм с пагинацией
        if movie_data:
            send_history_page(message, chat_id, movie_data, 1)
        else:
            bot.send_message(chat_id, "История поиска пуста.")
    else:
        bot.send_message(chat_id, "История поиска отсутствует.")


# Функция для отображения страницы с фильмом из истории
def send_history_page(message, chat_id, movie_data, page=1):
    total_pages = len(movie_data)
    current_data = movie_data[page - 1]  # Получаем текущий фильм и дату
    movie = current_data['movie']
    search_date = current_data['date']  # Дата запроса

    movie_info = (
        f"Название: {movie.title}\n"
        f"Описание: {movie.description[:200]}...\n"  # Показываем только первые 200 символов
        f"Год: {movie.year}\n"
        f"Рейтинг: {movie.rating}\n"
        f"Жанр: {movie.genre}\n"
        f"Возрастной рейтинг: {movie.age_rating}\n"
        f"Постер: {movie.poster_url}\n"
        f"Дата запроса: {search_date.strftime('%Y-%m-%d %H:%M:%S')}\n"  # Выводим дату и время запроса
    )

    # Создаем пагинацию для истории
    paginator = InlineKeyboardPaginator(
        total_pages,
        current_page=page,
        data_pattern='history#{page}'
    )

    if page > 1:
        paginator.add_before(InlineKeyboardButton('⬅️ Назад', callback_data=f'history#{page-1}'))

    if page < total_pages:
        paginator.add_after(InlineKeyboardButton('➡️ Вперед', callback_data=f'history#{page+1}'))

    bot.send_message(chat_id, movie_info, reply_markup=paginator.markup, parse_mode='Markdown')


# Обработчик для переключения между страницами в истории
@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'history')
def history_page_callback(call):
    page = int(call.data.split('#')[1])
    chat_id = call.message.chat.id

    # Получаем историю снова, чтобы перезагрузить данные для пагинации
    history_records = SearchHistory.select().where(SearchHistory.user_id == chat_id).order_by(SearchHistory.date.desc())
    movie_data = []
    for record in history_records:
        # Извлекаем все фильмы, содержащие текст запроса
        movies = Movie.select().where(Movie.title.contains(record.query))
        for movie in movies:
            movie_data.append({
                'movie': movie,
                'date': record.date  # Добавляем дату запроса
            })

    bot.delete_message(chat_id, call.message.message_id)  # Удаляем предыдущее сообщение
    send_history_page(call.message, chat_id, movie_data, page)
