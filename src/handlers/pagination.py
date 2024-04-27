from typing import Optional
from aiogram import Router
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from utils.pagination import pagination, Pagination, paginationTypeText
from config import decorate_logging
from utils import utils_func

router = Router(name='pagination')


@router.callback_query(Pagination.filter())
@decorate_logging
async def pagination_handler(callback: CallbackQuery, callback_data: Pagination, session: AsyncSession) -> None:
    """Pagination Handler"""
    await utils_func.delete_before_message(callback)
    page: int = callback_data.page
    type_: str = callback_data.type
    type_user: str = callback_data.permission
    status: Optional[str] = callback_data.status

    # Get Pagination Type
    pagination_type: tuple = paginationTypeText.get(
        type_,
        paginationTypeText.get('order')
    ).get(type_user)
    await pagination(
        page=page,
        type_=type_,
        status=status,
        session=session,
        message=callback.message,
        callback_back=pagination_type[2],
        callback_type=type_user,
        user_id=callback.from_user.id,
    )

