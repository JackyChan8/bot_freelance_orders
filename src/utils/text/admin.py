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

NOT_FOUND_COMMAND = 'Неизвестная Команда'
