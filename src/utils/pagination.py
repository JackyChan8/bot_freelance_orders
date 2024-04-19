from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.types import Message

from services import services as service_user


paginationTypeText: dict = {
    'order': ('📦 Заказ', service_user.get_my_orders)
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

    for data_id in data[start_offset:end_offset]:
        builder.row(
            InlineKeyboardButton(
                text=f'{paginationTypeText.get(type_)[0]} №{data_id}', callback_data=f'order_user_№{data_id}'
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
    await message.answer('Ваши Заказы:', reply_markup=builder.as_markup())
