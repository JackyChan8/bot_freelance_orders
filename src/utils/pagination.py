from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from services import services


paginationTypeText: dict = {
    'order': {
        'user': ('📦 Заказ', services.get_my_orders, 'back_to_profile', services.get_count_orders_by_user_id),
        'admin': ('📦 Заказ', services.get_orders_by_status, 'back_to_orders', services.get_count_orders_by_status),
    },
    'promocode': {
        'user': (
            '🎟 Промокод',
            services.get_promo_codes_by_user_id,
            'back_to_profile',
            services.get_count_promo_codes_by_user_id,
        ),
        'admin': ('🎟 Промокод', services.get_promo_codes, 'back_to_promo_code', services.get_count_promo_codes),
    },
    'review': {
        'user': ('🗒 Отзыв', services.get_reviews_by_user_id, 'our_reviews', services.get_count_reviews_by_user_id),
        'admin': ('🗒 Отзыв', services.get_reviews, 'back_to_reviews', services.get_count_reviews),
    },
    'users': {
        'admin': ('👤 Пользователи', services.get_users, 'back_to_users', services.get_count_users)
    }
}


class Pagination(CallbackData, prefix="pag"):
    action: str  # Действие
    page: int  # Номер страницы
    type: str  # Тип Пагинации
    permission: str  # Тип Пользователя
    status: Optional[str]  # Статус


async def pagination(type_: str,
                     message: Message,
                     session: AsyncSession,
                     page: int = 0,
                     callback_back: str = 'back_to_profile',
                     callback_type: str = 'user',
                     status: str = None,
                     user_id: int = None) -> None:
    builder = InlineKeyboardBuilder()
    limit: int = 3
    start_offset: int = page * 3
    end_offset: int = start_offset + limit

    pagination_type = paginationTypeText.get(
        type_,
        paginationTypeText.get('order')
    ).get(callback_type)

    # Get Data
    if callback_type == 'admin':
        data = await pagination_type[1](status, session=session, offset=start_offset)
        count = await pagination_type[-1](status, session=session)
    else:
        data = await pagination_type[1](user_id, session, offset=start_offset)
        count = await pagination_type[-1](user_id, session)

    for data_id in data:
        if type_ == 'users':
            author = await message.bot.get_chat_member(data_id, data_id)
            button_text = f'{pagination_type[0][0]} {author.user.username}'
        else:
            button_text = f'{pagination_type[0]} №{data_id}'
        builder.row(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f'{type_}_{callback_type}_№{data_id}',
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

    if end_offset < count:  # Проверка, что ещё есть пользователи для следующей страницы
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
    message_text = f'Ваши {pagination_type[0].split(' ')[-1]}{"" if type_ == "users" else "ы"}'
    await message.answer(
        message_text,
        reply_markup=builder.as_markup()
    )
