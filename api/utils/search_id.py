import os
from dotenv import load_dotenv
import requests
from urllib.parse import quote

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем API ключ из переменной окружения
API_KEY = os.getenv("API_KEY")

# Функция для поиска фильма по имени и возврата только ID фильмов
def search_movie_by_name(movie_name, limit=5):
    # Определяем количество фильмов, которые хотим запросить: всегда не менее 5
    api_limit = max(5, limit)

    # Кодируем название фильма для безопасной передачи в URL
    encoded_movie_name = quote(movie_name)

    # URL для поиска фильма с закодированным названием
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit={api_limit}&query={encoded_movie_name}"

    # Заголовки с API-ключом
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_KEY  # Теперь ключ берется из переменной окружения
    }

    # Выполняем запрос к API
    response = requests.get(url, headers=headers)

    # Проверяем успешность запроса
    if response.status_code == 200:
        data = response.json()

        # Проверяем наличие поля 'docs' в ответе
        if "docs" in data:
            # Извлекаем ID фильмов
            movie_ids = [movie['id'] for movie in data['docs'] if 'id' in movie]
            return movie_ids
        else:
            print("Поле 'docs' отсутствует в ответе")
            return []

    else:
        # Если произошла ошибка при запросе
        print(f"Ошибка {response.status_code}: {response.text}")
        return []
