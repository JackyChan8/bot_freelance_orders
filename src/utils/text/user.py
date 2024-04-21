from typing import Optional
from aiogram.utils.formatting import Bold

from config import settings

EMOJI_STATUS = {
    'Рассмотрение': '🟠',
    'Согласование': '🟡',
    'В работе': '🔵',
    'Тестирование': '🟣',
    'Завершенный': '🟢',
}


START_TEXT = """
👋 Добро пожаловать! 👋

🎉 Мы рады, что вы выбрали нас для разработки вашего сайта или приложения.

ℹ️ Наша команда профессионалов готова предоставить вам высококачественные услуги, которые помогут вам достичь ваших целей.

📝 Мы предлагаем широкий спектр услуг, включая разработку веб-сайтов, создание ботов, написание скриптов для различных платформ и многое другое.

🎯 Наша цель - помочь вам создать уникальный и функциональный продукт, который будет отвечать всем вашим требованиям и ожиданиям.

⏳ Мы ждем возможности обсудить ваши идеи и потребности подробнее.

🤝 С нетерпением ждем начала нашего сотрудничества!
"""

PROFILE_TEXT = """
💙 Пользователь: @{username}
💎 Количество заказов: {count_orders}
👤 ID: {user_id}
"""

# ================================================================= Create Order
CREATE_ORDER_TEXT_INFO = """
Привет, @{username}.

Чтобы начать работу над вашим приложением, мне нужно получить некоторую информацию.

Пожалуйста ответьте на следующие вопросы.
"""

CREATE_ORDER_TEXT_TYPE_APP = Bold('Какой тип приложения вы хотите разработать?')
CREATE_ORDER_TEXT_DESCRIPTION_APP = Bold("""
Пожалуйста, опишите свою идею подробно.
Какие функции и возможности вы хотите включить?
Какое впечатление вы хотите создать у пользователей?
""")
CREATE_ORDER_TEXT_TECH_TASK = Bold("""
Если у вас уже есть техническое задание или требования к приложению, пожалуйста, приложите его в виде файла.
Это поможет нам лучше понять ваши потребности и начать разработку.
""")
CREATE_ORDER_TEXT_UPLOAD_TECH_TASK = Bold('Отправьте ваше Техническое задание')
CREATE_ORDER_TEXT_FINISH = """
Спасибо за предоставленную информацию!
Мы свяжемся с вами в ближайшее время для уточнения деталей.
"""
NOT_EXISTS_ORDERS = 'У вас нет заказов'
NOTIFY_NEW_ORDER = 'ℹ️ Пришел новый заказ ℹ️'

"<span style=\"color:#fc5252;\">text</span>"


async def show_info_order(order_id: int, order_type: str, order_status: str,
                          description: str, order_created: str, discount: Optional[int] = None) -> str:
    """Show Information by Order"""
    return f"""
#️⃣ <b>Номер Заказа:</b> {order_id}
📑 <b>Тип:</b> {order_type}
{EMOJI_STATUS.get(order_status)} <b>Статус:</b> {order_status}
📄 <b>Описание:</b> {description}
🏷 <b>Промокод:</b> {f'{discount}%' if discount else 'Отсутствует'}
🕔 <b>Дата Создания:</b> {order_created}"""
# ================================================================= Referral System

FOUND_PARTNERS_TEXT = """
👨‍💻 Привет, дорогой {username}!

У тебя есть знакомые, которым нужно разработать сайт, бот, скрипт? Тогда наш бот для тебя!

🌐 Реферальная программа:

1. Поделись ссылкой на нашего бота с коллегами и друзьями, которым нужно разработать приложение.
2. Каждый, кто перейдет по твоей ссылке и сделает заказ, принесет тебе вознаграждение.
3. За каждого приглашенного друга ты получишь 10% от суммы его заказа.

Не упусти свой шанс! Приглашай коллег и друзей и получай денежное вознаграждение! 🚀

Ваша реферальная ссылка:
https://t.me/{bot_username}?start={referral_link}
"""

REFERRAL_SYSTEM_INFO = """
Общее количество рефералов: {count_referral}
Ваши рефералы:
{users}
"""

REFERRAL_SYSTEM_HISTORY_PAY = """
Общее количество пополнений: {count_pay}
История начислений:
"""

# ================================================================= Promo Codes
NOT_EXISTS_PROMO_CODES = 'У вас нет промокодов'
PROMO_CODE_EXIST_ORDER = '❗️ Вы не можете применить несколько промокодов для одного заказа ❗️'
PROMO_CODE_SUCCESS_APPLY = '🎉 Промокод успешно использован 🎉'
PROMO_CODE_IS_NOT_ACTIVE = '❗️ Промокод был удален ❗️'


async def show_info_promo_code(promo_code_id: int, discount: int, promo_code_created: str) -> str:
    """Show Information by Promo Code"""
    return f"""
#️⃣ <b>Номер Промокода:</b> {promo_code_id}
🏷 <b>Скидка:</b> {discount}%
🕔 <b>Дата Создания:</b> {promo_code_created}
"""

# ================================================================= Reviews
CREATE_REVIEW_MESSAGE = Bold('Пожалуйста, напишите ваш отзыв')
CREATE_REVIEW_RATING = Bold('Выберите рейтинг')
CREATE_REVIEW_SUCCESS = '🎉 Отзыв успешно оставлен 🎉'
NOT_EXISTS_REVIEWS = 'Отзывы отсутствуют'


async def show_info_review(review_id: int, author: str, text: str, rating: int, review_created: str) -> str:
    """Show Information by Review"""
    return f"""
#️⃣ <b>Номер Отзыва:</b> {review_id}
👤 <b>Автор:</b> @{author}
📄 <b>Текст:</b> {text}
🎖 <b>Рейтинг:</b> {rating}
🕔 <b>Дата Публикации:</b> {review_created}"""
# =================================================================

ABOUT_US_TEXT = """
Мы команда разработчиков
"""

SUPPORT_TEXT = """
Есть вопрос или нужна помощь? - @{username}

Не нашлось решения вопроса с тех.поддержкой? - Email администрации проекта: {email}
""".format(username=settings.USERNAME_ADMIN, email=settings.EMAIL_ADMIN)

REVIEWS_TEXT = """
Пожалуйста выберите подходящую команду
"""

NOT_FOUND_COMMAND = 'Неизвестная Команда'
NOT_USE_SELF_REFERRAL_LINK = '❗️ Нельзя регистрироваться по собственной реферальной ссылке ❗️'
SUCCESS_CREATE_BY_REFERRAL_LINK = """
🎉 Пользователь @{username} успешно зарегистрировался в боте по вашей реферальной ссылке 🎉
"""
