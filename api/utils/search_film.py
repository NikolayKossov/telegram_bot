import os
from dotenv import load_dotenv
import requests

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение API-ключа из переменной окружения
API_KEY = os.getenv("API_KEY")

# Функция для фильтрации по жанрам
def filter_by_genres(movie, genres):
    if not genres:  # Если жанры не передаются, фильтрация не нужна
        return True

    # Проверяем, есть ли пересечение жанров фильма с переданными жанрами
    movie_genres = [genre['name'].lower() for genre in movie.get('genres', [])]
    genres_lower = [g.lower() for g in genres]

    return any(genre in movie_genres for genre in genres_lower)  # Возвращаем True, если есть совпадения

# Функция для получения фильма по ID и фильтрации по жанрам
def get_movie_by_id(movie_id, genres=None):
    # URL для запроса фильма по ID
    url = f"https://api.kinopoisk.dev/v1.4/movie/{movie_id}"

    # Заголовки для запроса
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_KEY
    }

    # Параметры запроса
    params = {
        "selectFields": ["name", "description", "rating", "year", "genres", "ageRating", "poster"],
        "sortField": "",
        "sortType": -1
    }

    # Выполняем запрос к API напрямую с использованием requests
    response = requests.get(url, headers=headers, params=params)

    # Проверяем успешность запроса
    if response.status_code == 200:
        movie_data = response.json()

        # Проверяем жанры, если они переданы
        if filter_by_genres(movie_data, genres):
            return movie_data
        else:
            return None  # Возвращаем None, если жанры не совпали
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return None  # Возвращаем None, если произошла ошибка при запросе
