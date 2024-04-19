from aiogram.types import Message
from sqlalchemy import select, insert, exists, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models import Users, Orders, ReferralSystem
from utils.text import user as user_text
from utils.keyboards.reply import user as user_reply_keyboard


# ================================================================= Users
async def check_exist_user(user_id: int, session: AsyncSession) -> bool:
    """Check Exists User"""
    result = await session.execute(
        select(exists(Users.id).where(Users.id == user_id))
    )
    return result.scalar()


async def create_user(user_id: int, username: str, message: Message, session: AsyncSession):
    """Create User Service"""
    query = (
        insert(Users)
        .values(id=user_id, username=username)
    )
    try:
        await session.execute(query)
        await session.commit()
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при создании пользователя')
        await message.answer(str(exc))


# ================================================================= Orders
async def get_count_orders(user_id: int, session: AsyncSession) -> int:
    """Get Count Orders Service"""
    result = await session.execute(
        select(func.count("*")).select_from(Orders).where(Orders.customer == user_id)
    )
    return result.scalar()


async def get_filename_task_tech(order_id: int, session: AsyncSession) -> str:
    """Get Filename Task Tech Service"""
    query = (
        select(Orders.tech_task_filename)
        .where(Orders.id == order_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_my_order(user_id: int, order_id: int, session: AsyncSession):
    """Get Order Service"""
    query = (
        select(Orders)
        .where(Orders.id == order_id, Orders.customer == user_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_my_orders(user_id: int, session: AsyncSession):
    """Get Orders Service"""
    query = (
        select(Orders.id)
        .where(Orders.customer == user_id)
        .order_by(desc(Orders.id))
    )
    result = await session.execute(query)
    return result.scalars().all()


async def create_order(user_id: int, order_type: str, description: str, tech_task_filename: str | None,
                       message: Message, session: AsyncSession) -> None:
    """Create Order Service"""
    buttons = await user_reply_keyboard.start_reply_keyboard()
    query = (
        insert(Orders)
        .values(
            customer=user_id,
            type=order_type,
            description=description,
            tech_task_filename=tech_task_filename,
        )
    )
    try:
        await session.execute(query)
        await session.commit()
        await message.answer(user_text.CREATE_ORDER_TEXT_FINISH, reply_markup=buttons)
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при создании заказа')
        await message.answer(str(exc), reply_markup=buttons)


# ================================================================= Referral System
async def get_count_refer_link(user_id: int, session: AsyncSession) -> int:
    """Get Count Referral Links Service"""
    result = await session.execute(
        select(func.count("*")).select_from(ReferralSystem).where(ReferralSystem.referral_id == user_id)
    )
    return result.scalar()


async def get_referral_users_id(user_id: int, session: AsyncSession):
    """Get Referral Users ID Service"""
    query = (
        select(ReferralSystem.user_id)
        .where(ReferralSystem.referral_id == user_id)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def create_refer_link(user_id: int, referral_id: int, session: AsyncSession) -> bool:
    """Create Referral Link Service"""
    query = (
        insert(ReferralSystem)
        .values(
            user_id=user_id,
            referral_id=referral_id,
        )
    )
    try:
        await session.execute(query)
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        return False
