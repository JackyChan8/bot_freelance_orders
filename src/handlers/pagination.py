from typing import Optional
from aiogram import Router
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from utils.pagination import pagination, Pagination, paginationTypeText
from utils import utils_func

router = Router(name='pagination')


@router.callback_query(Pagination.filter())
async def pagination_handler(callback: CallbackQuery, callback_data: Pagination, session: AsyncSession) -> None:
    """Pagination Handler"""
    await utils_func.delete_before_message(callback)
    page: int = callback_data.page
    type_: str = callback_data.type
    type_user: str = callback_data.permission
    status: Optional[str] = callback_data.status

    # Get From Database Data
    type_text: tuple = paginationTypeText.get(
        type_,
        paginationTypeText.get('order').get(type_user)
    ).get(type_user)
    if type_user == 'admin':
        data = await type_text[1](status, session)
    else:
        data = await type_text[1](callback.from_user.id, session)
    callback_data: str = type_text[2]
    await pagination(
        data=data,
        page=page,
        type_=type_,
        status=status,
        message=callback.message,
        callback_back=callback_data,
        callback_type=type_user,
    )

