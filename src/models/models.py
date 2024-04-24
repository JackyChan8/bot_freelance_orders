from datetime import datetime
from typing import Optional, Literal, get_args

from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, BigInteger, String, Text, Boolean, ForeignKey, CheckConstraint, Date, Enum

from .base_class import Base


OrderStatus = Literal['Рассмотрение', 'Согласование', 'В работе', 'Тестирование', 'Завершенный']
OrderType = Literal['Веб-Сайт', 'Telegram Bot', 'Работа с серверами', 'Верстка', 'Скрипт']


class Users(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    is_ban: Mapped[bool] = mapped_column(Boolean, default=False)


class Reviews(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author: Mapped[int] = mapped_column(ForeignKey('users.id'))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    is_publish: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(Date, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(Date, default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(rating >= 0, name='check_rating_positive'),
        CheckConstraint(rating <= 5, name='check_rating_not_more_five')
    )


class Orders(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer: Mapped[int] = mapped_column(ForeignKey('users.id'))
    type: Mapped[OrderType] = mapped_column(Enum(
        *get_args(OrderType),
        name='ordertype',
        create_constraint=True,
        validate_strings=True,
    ))
    status: Mapped[OrderStatus] = mapped_column(Enum(
        *get_args(OrderStatus),
        name='orderstatus',
        create_constraint=True,
        validate_strings=True,
    ), default=get_args(OrderStatus)[0])
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tech_task_filename: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(Date, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(Date, default=func.now(), onupdate=func.now())


class ReferralSystem(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    referral_id: Mapped[int] = mapped_column(ForeignKey('users.id'))


class PromoCode(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=True, default=None)
    discount: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(Date, default=func.now())

    __table_args__ = (
        CheckConstraint(discount > 0, name='check_positive_discount'),
        CheckConstraint(discount < 100, name='check_not_more_100_discount'),
    )


class Projects(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technology: Mapped[str] = mapped_column(Text, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(Date, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(Date, default=func.now(), onupdate=func.now())


class Images(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(Date, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(Date, default=func.now(), onupdate=func.now())
