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

# Функция для получения фильмов с сортировкой по бюджету и фильтрацией по жанрам
def get_high_budget_movies(name, limit=10, genres=None):
    # URL для поиска фильмов
    url = f"https://api.kinopoisk.dev/v1.4/movie/search"

    # Заголовки для запроса
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_KEY
    }

    # Параметры запроса
    params = {
        "query": name,
        "page": 1,
        "limit": 50,  # Запрашиваем больше фильмов для увеличения вероятности получения фильмов с высоким бюджетом
        "selectFields": ["name", "description", "rating", "year", "genres", "ageRating", "poster", "budget"],
        "sortField": "budget.value",  # Сортировка по бюджету
        "sortType": -1  # По убыванию бюджета
    }

    # Выполняем запрос к API
    response = requests.get(url, headers=headers, params=params)

    # Проверяем успешность запроса
    if response.status_code == 200:
        movies_data = response.json().get('docs', [])

        # Фильтруем фильмы по жанрам, если они указаны
        filtered_movies = [movie for movie in movies_data if filter_by_genres(movie, genres)]

        # Ограничиваем до указанного лимита
        filtered_movies = filtered_movies[:limit]

        if not filtered_movies:
            print("Фильмы не найдены после фильтрации по жанрам.")
        else:
            print(f"Найдено фильмов после фильтрации: {len(filtered_movies)}")

        # Логирование для отладки
        for movie in filtered_movies:
            print(f"Фильм: {movie['name']}, Бюджет: {movie.get('budget', {}).get('value', 'Не указан')}")

        return filtered_movies
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return []

