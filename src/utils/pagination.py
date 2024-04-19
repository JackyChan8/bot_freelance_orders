from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.types import Message

from services import services as service_user


paginationTypeText: dict = {
    'order': ('📦 Заказ', service_user.get_my_orders),
    'promocode': ('🎟 Промокод', service_user.get_promo_codes),
}


class Pagination(CallbackData, prefix="pag"):
    action: str  # Действие
    page: int  # Номер страницы
    type: str  # Тип Пагинации


async def pagination(data: list, type_: str, message: Message, page=0) -> None:
    builder = InlineKeyboardBuilder()
    start_offset: int = page * 3
    limit: int = 3
    end_offset: int = start_offset + limit

    type_text = paginationTypeText.get(
        type_,
        paginationTypeText.get('order')
    )[0]

    for data_id in data[start_offset:end_offset]:
        builder.row(
            InlineKeyboardButton(
                text=f'{type_text} №{data_id}', callback_data=f'{type_}_user_№{data_id}'
            )
        )

    buttons_row: list = []
    if page > 0:  # Проверка, что страница не первая
        buttons_row.append(InlineKeyboardButton(
            text="⬅️", callback_data=Pagination(action="prev", page=page - 1, type=type_).pack())
        )
    if end_offset < len(data):  # Проверка, что ещё есть пользователи для следующей страницы
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=page + 1, type=type_).pack())
        )
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='« Назад', callback_data='back_to_profile'))
    await message.answer(
        f'Ваши {type_text.split(' ')[-1]}ы:',
        reply_markup=builder.as_markup()
    )
