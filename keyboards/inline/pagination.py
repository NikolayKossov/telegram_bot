from telebot.types import InlineKeyboardButton
from telegram_bot_pagination import InlineKeyboardPaginator

# Функция для создания пагинации с кнопками "Вперед" и "Назад"
def create_movie_pagination(current_page, total_pages):
    paginator = InlineKeyboardPaginator(
        total_pages,  # Общее количество страниц (фильмов)
        current_page=current_page,  # Текущая страница
        data_pattern='movie#{page}'  # Шаблон для передачи данных о странице
    )

    # Добавляем кнопки "Назад" и "Вперед"
    paginator.add_before(
        InlineKeyboardButton('⬅️ Назад', callback_data=f'movie#{current_page-1}') if current_page > 1 else None
    )
    paginator.add_after(
        InlineKeyboardButton('➡️ Вперед', callback_data=f'movie#{current_page+1}') if current_page < total_pages else None
    )

    return paginator.markup
