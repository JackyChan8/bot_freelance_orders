from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.types import Message

from services import services


paginationTypeText: dict = {
    'order': {
        'user': ('📦 Заказ', services.get_my_orders, 'back_to_profile'),
        'admin': ('📦 Заказ', services.get_orders_by_status, 'back_to_orders'),
    },
    'promocode': {
        'user': ('🎟 Промокод', services.get_promo_codes_by_user_id, 'back_to_profile'),
        'admin': ('🎟 Промокод', services.get_promo_codes, 'back_to_promo_code'),
    },
    'review': {
        'user': ('🗒 Отзыв', services.get_reviews, 'our_reviews'),
        'admin': (),
    }
}


class Pagination(CallbackData, prefix="pag"):
    action: str  # Действие
    page: int  # Номер страницы
    type: str  # Тип Пагинации
    permission: str  # Тип Пользователя
    status: Optional[str]  # Статус


async def pagination(data: list,
                     type_: str,
                     message: Message,
                     page: int = 0,
                     callback_back: str = 'back_to_profile',
                     callback_type: str = 'user',
                     status: str = None) -> None:
    builder = InlineKeyboardBuilder()
    start_offset: int = page * 3
    limit: int = 3
    end_offset: int = start_offset + limit

    pagination_type = paginationTypeText.get(
        type_,
        paginationTypeText.get('order')
    ).get(callback_type)[0]

    for data_id in data[start_offset:end_offset]:
        builder.row(
            InlineKeyboardButton(
                text=f'{pagination_type} №{data_id}', callback_data=f'{type_}_{callback_type}_№{data_id}'
            )
        )

    buttons_row: list = []
    if page > 0:  # Проверка, что страница не первая
        buttons_row.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=Pagination(
                action="prev",
                page=page - 1,
                type=type_,
                permission=callback_type,
                status=status,
            ).pack()
        )
        )
    if end_offset < len(data):  # Проверка, что ещё есть пользователи для следующей страницы
        buttons_row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=Pagination(
                    action="next",
                    page=page + 1,
                    type=type_,
                    permission=callback_type,
                    status=status,
                ).pack()
            )
        )
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='« Назад', callback_data=callback_back))
    await message.answer(
        f'Ваши {pagination_type.split(' ')[-1]}ы:',
        reply_markup=builder.as_markup()
    )
