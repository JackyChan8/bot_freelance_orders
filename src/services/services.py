from typing import Any

from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy import select, insert, update, exists, func, desc, case, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import true, false, null

from models import Users, Orders, ReferralSystem, PromoCode, Reviews
from utils.text import user as user_text
from utils.text import admin as admin_text
from utils.keyboards.reply import user as user_reply_keyboard
from utils.utils_func import statuses


# ================================================================= Users
async def check_exist_user_by_id(user_id: int, session: AsyncSession) -> bool:
    """Check Exists User By ID"""
    result = await session.execute(
        select(exists(Users.id).where(Users.id == user_id))
    )
    return result.scalar()


async def check_exist_user_by_username(username: str, session: AsyncSession) -> bool:
    """Check Exists User By Username"""
    result = await session.execute(
        select(exists(Users.id).where(Users.username == username))
    )
    return result.scalar()


async def get_user_id_by_username(username: str, session: AsyncSession) -> int:
    """Get User ID By Username"""
    query = (
        select(Users.id)
        .where(Users.username == username)
    )
    result = await session.execute(query)
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
async def get_count_orders_by_user_id(user_id: int, session: AsyncSession) -> int:
    """Get Count Orders By User ID Service"""
    result = await session.execute(
        select(func.count("*")).select_from(Orders).where(Orders.customer == user_id)
    )
    return result.scalar()


async def get_count_orders_by_status(status: str, session: AsyncSession) -> int:
    """Get Count Orders By Status Service"""
    result = await session.execute(
        select(func.count('*')).select_from(Orders).where(Orders.status == statuses.get(status))
    )
    return result.scalar()


async def get_count_by_status(session: AsyncSession):
    """Get Count Orders by Status"""
    query = (
        select(
            func.count(Orders.id).label('total'),
            func.count(case((Orders.status == 'Рассмотрение', 1))).label('new'),
            func.count(case((Orders.status == 'Согласование', 1))).label('coordination'),
            func.count(case((Orders.status == 'В работе', 1))).label('work'),
            func.count(case((Orders.status == 'Тестирование', 1))).label('test'),
            func.count(case((Orders.status == 'Завершенный', 1))).label('finish')
        )
    )
    result = await session.execute(query)
    return result.fetchone()


async def get_orders_by_status(status: str, session: AsyncSession, offset: int = null(), limit: int = 3):
    """Get Orders by Status"""
    query = (
        select(Orders.id)
        .where(Orders.status == statuses.get(status))
        .limit(limit)
        .offset(offset)
        .order_by(desc(Orders.id))
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_customer_by_order(order_id: int, session: AsyncSession) -> Row[tuple[Any, Any]] | None:
    """Get Customer by Order ID Service"""
    query = (
        select(Users.id, Users.username)
        .select_from(Orders)
        .join(Users, Users.id == Orders.customer)
        .where(Orders.id == order_id)
    )
    result = await session.execute(query)
    return result.first()


async def get_filename_task_tech(order_id: int, session: AsyncSession) -> str:
    """Get Filename Task Tech Service"""
    query = (
        select(Orders.tech_task_filename)
        .where(Orders.id == order_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_my_order(user_id: int, order_id: int, session: AsyncSession):
    """Get My Order Service"""
    query = (
        select(Orders)
        .where(Orders.id == order_id, Orders.customer == user_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_order(order_id: int, session: AsyncSession):
    """Get Order Service"""
    query = (
        select(Orders)
        .where(Orders.id == order_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_order_status(order_id: int, session: AsyncSession):
    """Get Order Status Service"""
    query = (
        select(Orders.status)
        .where(Orders.id == order_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_my_orders(user_id: int, session: AsyncSession, offset: int = null(), limit: int = 3):
    """Get Orders Service"""
    query = (
        select(Orders.id)
        .where(Orders.customer == user_id)
        .limit(limit)
        .offset(offset)
        .order_by(desc(Orders.id))
    )
    result = await session.execute(query)
    return result.scalars().all()


async def change_status_order(order_id: int, status: str, message: Message, session: AsyncSession) -> bool:
    """Change Status Order Service"""
    query = (
        update(Orders)
        .where(Orders.id == order_id)
        .values(status=statuses.get(status))
        .execution_options(synchronize_session='fetch')
    )
    try:
        await session.execute(query)
        await session.commit()
        await message.answer(admin_text.CHANGE_SUCCESS_ORDER_TEXT)
        return True
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при изменении статуса заказа')
        await message.answer(str(exc))
        return False


async def create_order(user_id: int, order_type: str, description: str, tech_task_filename: str | None,
                       message: Message, session: AsyncSession) -> bool:
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
        return True
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при создании заказа')
        await message.answer(str(exc), reply_markup=buttons)
        return False


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


# ================================================================= Promo Code
async def create_promo_code(user_id: int, discount: int, message: Message, session: AsyncSession) -> bool:
    """Create Promo Code Service"""
    query = (
        insert(PromoCode)
        .values(
            user_id=user_id,
            discount=discount,
        )
    )
    try:
        await session.execute(query)
        await session.commit()
        await message.answer(admin_text.PROMO_CODE_CREATE_TEXT)
        return True
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при создании промокода', reply_markup=ReplyKeyboardRemove())
        await message.answer(str(exc))
        return False


async def get_count_promo_codes(*args, session: AsyncSession) -> int:
    """Get Count Promo Codes"""
    result = await session.execute(
        select(func.count('*')).select_from(PromoCode)
    )
    return result.scalar()


async def get_count_promo_codes_by_user_id(user_id: int, session: AsyncSession) -> int:
    """Get Count Promo Codes By User ID"""
    result = await session.execute(
        select(func.count('*'))
        .select_from(PromoCode)
        .where(PromoCode.user_id == user_id)
    )
    return result.scalar()


async def check_exists_promo_code_order(user_id: int, order_id: int, session: AsyncSession) -> bool:
    """Check Exist Active Promo Code in Order"""
    result = await session.execute(
        select(exists(PromoCode.id))
        .where(
            PromoCode.user_id == user_id,
            PromoCode.order_id == order_id
        )
    )
    return result.scalar()


async def check_is_active_promo_code(promo_code_id: int, session: AsyncSession) -> bool:
    """Check is Active Promo Code"""
    result = await session.execute(
        select(exists(PromoCode.id))
        .where(
            PromoCode.id == promo_code_id,
            PromoCode.is_active == true(),
        )
    )
    return result.scalar()


async def get_promo_code_for_order(order_id: int, session: AsyncSession):
    """Get Promo Code for Order"""
    query = (
        select(PromoCode.discount)
        .where(PromoCode.order_id == order_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_my_promo_code(user_id: int, promo_code_id: int, session: AsyncSession):
    """Get My Promo Code Servicec"""
    query = (
        select(PromoCode)
        .where(PromoCode.id == promo_code_id, PromoCode.user_id == user_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_promo_codes_by_user_id(user_id: int, session: AsyncSession, offset: int = null(), limit: int = 3):
    """Get Promo Codes By User ID Service"""
    query = (
        select(PromoCode.id)
        .where(
            PromoCode.user_id == user_id,
            PromoCode.is_active == true(),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_owner_promo_code(promo_code_id: int, session: AsyncSession) -> Row[tuple[Any, Any]] | None:
    """Get Information Owner by Promo Code"""
    query = (
        select(Users.id, Users.username)
        .select_from(PromoCode)
        .join(Users, Users.id == PromoCode.user_id)
        .where(PromoCode.id == promo_code_id)
    )
    result = await session.execute(query)
    return result.first()


async def get_promo_code_by_id(promo_code_id: int, session: AsyncSession):
    """Get Promo Code By ID Service"""
    query = (
        select(PromoCode)
        .where(PromoCode.id == promo_code_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def get_promo_codes(*args, session: AsyncSession, offset: int = null(), limit: int = 3):
    """Get Promo Codes Service"""
    query = (
        select(PromoCode.id)
        .where(PromoCode.is_active == true())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def apply_promo_code(user_id: int, promo_code_id: int, order_id: int,
                           message: Message, session: AsyncSession) -> None:
    """Apply promo code to order"""
    query = (
        update(PromoCode)
        .where(
            PromoCode.id == promo_code_id,
            PromoCode.user_id == user_id
        )
        .values(
            is_active=false(),
            order_id=order_id,
        )
        .execution_options(synchronize_session='fetch')
    )
    try:
        await session.execute(query)
        await session.commit()
        await message.answer(user_text.PROMO_CODE_SUCCESS_APPLY)
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при добавлении заказа в промокод')
        await message.answer(str(exc))


async def delete_promo_code(promo_code_id: int, message: Message, session: AsyncSession) -> None:
    """Delete promo code"""
    query = (
        update(PromoCode)
        .where(PromoCode.id == promo_code_id)
        .values(is_active=false())
        .execution_options(synchronize_session='fetch')
    )
    try:
        await session.execute(query)
        await session.commit()
        await message.answer(admin_text.DELETE_PROMO_CODE_TEXT)
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при удалении промокода')
        await message.answer(str(exc))


# ================================================================= Review
async def create_review(user_id: int, text: str, rating: int, message: Message, session: AsyncSession) -> None:
    """Create Review Service"""
    buttons = await user_reply_keyboard.start_reply_keyboard()
    query = (
        insert(Reviews)
        .values(
            author=user_id,
            message=text,
            rating=rating,
        )
    )
    try:
        await session.execute(query)
        await session.commit()
        await message.answer(user_text.CREATE_REVIEW_SUCCESS, reply_markup=buttons)
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при создании отзыва')
        await message.answer(str(exc), reply_markup=buttons)


async def get_count_reviews_by_user_id(user_id: int, session: AsyncSession) -> int:
    """Get Count Reviews By User ID"""
    result = await session.execute(
        select(func.count('*'))
        .select_from(Reviews)
        .where(Reviews.is_publish == true(), Reviews.author != user_id)
    )
    return result.scalar()


async def get_count_reviews(*args, session: AsyncSession) -> int:
    """Get Count Reviews"""
    result = await session.execute(
        select(func.count('*')).select_from(Reviews)
    )
    return result.scalar()


async def get_reviews(*args, session: AsyncSession, offset: int = null(), limit: int = 3):
    """Get Reviews Service"""
    query = (
        select(Reviews.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_reviews_by_user_id(user_id: int, session: AsyncSession, offset: int = null(), limit: int = 3):
    """Get Reviews By User ID Service"""
    query = (
        select(Reviews.id)
        .where(Reviews.is_publish == true(), Reviews.author != user_id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_review_by_id(review_id: int, session: AsyncSession):
    """Get Review By ID Service"""
    query = (
        select(Reviews)
        .where(Reviews.id == review_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def update_review_by_id(review_id: int, is_publish: bool, message: Message, session: AsyncSession) -> None:
    """Publish / UnPublish Review By ID"""
    text: str = await admin_text.update_review(is_publish)
    is_publish = true() if is_publish else false()

    query = (
        update(Reviews)
        .where(
            Reviews.id == review_id,
        )
        .values(
            is_publish=is_publish,
        )
        .execution_options(synchronize_session='fetch')
    )
    try:
        await session.execute(query)
        await session.commit()
        await message.answer(text)
    except Exception as exc:
        await session.rollback()
        await message.answer('Произошла ошибка при изменении отзыва')
        await message.answer(str(exc))
