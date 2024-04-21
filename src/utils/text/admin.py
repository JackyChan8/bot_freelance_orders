from utils.utils_func import statuses

PROMO_CODE_CREATE = "🎉 Промокод Успешно Создан 🎉"

START_TEXT = """
👋 Добро пожаловать в админку! 👋
"""

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
