from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def orders_inline_keyboard(order_id: Optional[int] = None) -> InlineKeyboardMarkup:
    callback_text = 'show_orders'
    if order_id:
        callback_text = f'save_choose_status_{order_id}'

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Новые Заказы', callback_data=f'new_{callback_text}'),
            ],
            [
                InlineKeyboardButton(text='На Согласовании', callback_data=f'coord_{callback_text}'),
                InlineKeyboardButton(text='В Работе', callback_data=f'work_{callback_text}'),
            ],
            [
                InlineKeyboardButton(text='На Тестировании', callback_data=f'test_{callback_text}'),
            ],
            [
                InlineKeyboardButton(text='Завершенные', callback_data=f'finish_{callback_text}'),
            ],
        ]
    )


async def get_order_info_inline_keyboard(order_id: int, is_task: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_task:
        builder.row(
            InlineKeyboardButton(text='📥 Скачать Техн.Задание', callback_data=f'download_file_order_{order_id}')
        )
    builder.row(
        InlineKeyboardButton(text='🔄 Изменить Статус', callback_data=f'change_status_order_{order_id}'),
        InlineKeyboardButton(text='👤 Показать Заказчика', callback_data=f'show_customer_order_{order_id}'),
        width=1
    )
    return builder.as_markup()
