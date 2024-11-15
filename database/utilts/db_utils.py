from database.common.models import SearchHistory, Movie

# Функция для сохранения запроса
def save_search(user_id, query):
    return SearchHistory.create(user_id=user_id, query=query)

# Функция для сохранения фильма
def save_movie(title, description, rating, year, genre, age_rating, poster_url):
    return Movie.create(
        title=title, 
        description=description,
        rating=rating,
        year=year,
        genre=genre,
        age_rating=age_rating,
        poster_url=poster_url
    )

# Функция для получения истории запросов
def get_user_history(user_id):
    return SearchHistory.select().where(SearchHistory.user_id == user_id)
