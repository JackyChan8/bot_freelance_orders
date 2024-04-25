from aiogram.utils.formatting import Bold

from utils.utils_func import statuses

START_TEXT = """
👋 Добро пожаловать в админку! 👋
"""

# ================================================================= Orders

ORDERS_TEXT = """
🗄 <b>Общее Количество Заказов:</b> {total_orders}
🟠 <b>Новых Заказов:</b> {total_new_orders}
🟡 <b>Заказов на Согласование:</b> {total_coord_orders}
🔵 <b>Заказов в Работе:</b> {total_work_orders}
🟣 <b>Заказов на Тестирование:</b> {total_test_orders}
🟢 <b>Завершенных Заказов:</b> {total_finish_orders}
"""

NOT_EXISTS_ORDERS_WITH_STATUS = 'У вас нет заказов с данным статусом'
CHANGE_STATUS_ORDER_TEXT = 'Выберите статус на который хотите сменить заказ'
CHANGE_SUCCESS_ORDER_TEXT = '🎉 Статус успешно изменен 🎉'
NOT_CHANGE_EXISTS_STATUS = '❗️ Вы не можете поставить данный статус т.к. он уже привязан к заказу ❗️'


async def notify_success_change_order(order_id: int, status: str):
    return f'ℹ️ Статус Вашего заказа №{order_id} изменен на {statuses.get(status)}'


# ================================================================= Promo Codes
PROMO_CODE_MENU_TEXT = 'Выберите подходящую команду'
PROMO_CODE_CREATE_TEXT = "🎉 Промокод Успешно Создан 🎉"
SET_USERNAME_PROMO_CODE_TEXT = Bold('Напишите имя пользователя в формате: username')
SET_DISCOUNT_PROMO_CODE_TEXT = Bold('Пожалуйста напишите % скидки в формате цифры')
SET_DISCOUNT_PROMO_CODE_RANGE = '❗️ Процент должен быть не меньше 0 и не больше 100 ❗️'
NOT_FOUND_USERNAME_PROMO_CODE_TEXT = '❗️ Пользователь с таким username не найден ❗️'
NOTIFY_PROMO_CODE_SUCCESS_ADD = 'ℹ️ Промокод был добавлен в ваш аккаунт. Скидка: {discount}% ℹ️'
NOT_EXISTS_PROMO_CODES = 'Промокоды отсутствуют'
DELETE_PROMO_CODE_TEXT = '🎉 Промокод успешно удален 🎉'

# ================================================================= Reviews
REVIEWS_MENU_TEXT = 'Выберите подходящую команду'
NOT_EXISTS_REVIEWS = 'Отзывы отсутствуют'


async def update_review(is_publish: bool) -> str:
    text = 'Опубликован' if is_publish else 'Снят с Публикации'
    return f'🎉 Отзыв успешно {text} 🎉'

NOT_FOUND_COMMAND = 'Неизвестная Команда'

# ================================================================= Users
USER_MENU_TEXT = 'Кол-во Пользователей: {count_users}'
NOT_EXISTS_USERS = 'Пользователи отсутствуют'

USER_INFO_TEXT = """
👤 <b>Имя Пользователя:</b> {username}
#️⃣ <b>Заказов</b> {count_orders}
📄 <b>Отзывов</b> {count_reviews}
🌐 <b>Рефералов</b> {count_referrals}
🏷 <b>Промокодов</b> {count_promo_codes}
"""


async def ban_user_text(is_ban: bool) -> str:
    text = 'Заблокирован' if is_ban else 'Разблокирован'
    return f'Пользователь {text}'

USER_BLOCK = '❗️ Вы были забанены ❗️'
USER_UN_BLOCK = '🎉 Вас разбанили 🎉'


# ================================================================= Settings
SETTINGS_MENU_TEXT = 'Выберите подходящую команду'

# ================================================================= Jobs
JOBS_TITLE_TEXT = Bold('Пожалуйста напишите название Проекта')
JOBS_TITLE_DESCRIPTION = Bold('Пожалуйста напишите описание Проекта')
JOBS_TITLE_TECHNOLOGY = Bold('Пожалуйста напишите технологии через запятую, которые были использованы в Проекте')
JOBS_TITLE_IMAGES = Bold('Добавьте фотографии Проекта')
JOB_SUCCESS_ADD = Bold('🎉 Проект был успешно добавлен 🎉')
NOT_EXISTS_JOBS = 'Работы отсутствуют'

JOBS_INFO_TEXT = """
📄 <b>Заголовок:</b> {title}
📃 <b>Описание</b> {description}
📋 <b>Технологии</b> {technology}
🕔 <b>Дата Публикации:</b> {project_created}
"""
JOBS_SUCCESS_CHANGE = '🎉 Проект был успешно изменен 🎉'
EDITED_PROJECT_TEXT = 'Пожалуйста добавьте фотографии проекта'


async def edited_project_text(field: str) -> str:
    fields_text = {
        'title': 'Заголовок',
        'description': 'Описание',
        'technology': 'Технологии',
    }
    return f'Пожалуйста напишите {fields_text.get(field)} проекта'


# ================================================================= Settings Studio
SETTINGS_STUDIO_MENU_TEXT = 'Выберите подходящую команду'
ADD_TECH_SUPPORT_USERNAME = Bold('Пожалуйста напишите Username Техн.Поддержки')
ADD_TECH_SUPPORT_EMAIL = Bold('Пожалуйста напишите Email Техн.Поддержки')
ADD_TECH_SUPPORT_SUCCESS = '🎉 Информация о Техн.Поддержки была успешно добавлена 🎉'
UPDATE_TECH_SUPPORT_SUCCESS = '🎉 Информация о Техн.Поддержки была успешно изменена 🎉'
TECH_SUPPORT_INFO = """
👤 <b>Пользователь:</b> @{username}
📧 <b>Email:</b> {email}
"""

NOT_VALID_EMAIL_TEXT = 'Введите правильный Email Адрес'
