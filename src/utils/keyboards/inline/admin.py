from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ================================================================= Orders

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


# ================================================================= Promo Codes
async def promo_code_inline_keyboards() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Показать промокоды', callback_data='show_promo_code')
            ],
            [
                InlineKeyboardButton(text='Создать промокод', callback_data=f'create_promo_code'),
            ],
        ]
    )


async def get_promo_code_info_inline_keyboard(promo_code_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='❌ Удалить промокод', callback_data=f'delete_promo_code_{promo_code_id}')
            ],
            [
                InlineKeyboardButton(text='👤 Показать Владельца', callback_data=f'show_promo_code_user_{promo_code_id}'),
            ],
        ]
    )


# ================================================================= Reviews
async def reviews_inline_keyboards() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='#️⃣ Показать Отзывы', callback_data=f'show_reviews')
            ]
        ]
    )


async def get_review_info_inline_keyboard(review_id: int, is_publish: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_publish:
        builder.row(
            InlineKeyboardButton(text='⬇️ Снять с публикации', callback_data=f'remove_public_review_{review_id}')
        )
    else:
        builder.row(
            InlineKeyboardButton(text='⬆️ Опубликовать', callback_data=f'add_public_review_{review_id}')
        )
    return builder.as_markup()


# ================================================================= Users
async def users_inline_keyboards() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='👥 Показать Пользователей', callback_data='show_users')
            ],
        ]
    )


async def get_user_info_inline_keyboard(user_id: int, is_ban: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_ban:
        builder.row(
            InlineKeyboardButton(text='⬆️ Разблокировать', callback_data=f'unblock_user_{user_id}')
        )
    else:
        builder.row(
            InlineKeyboardButton(text='⬇️ Заблокировать', callback_data=f'block_user_{user_id}')
        )
    return builder.as_markup()


# ================================================================= Settings
async def settings_inline_keyboards() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='🗄 Наши Работы', callback_data='our_jobs'),
            ],
            [
                InlineKeyboardButton(text='🏛 Студия', callback_data='settings_studio')
            ],
        ]
    )


async def add_our_works(is_jobs: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_jobs:
        builder.row(
            InlineKeyboardButton(text='✏️ Изменить Работу', callback_data='change_project')
        )
    builder.row(
        InlineKeyboardButton(text='➕ Добавить Работу', callback_data='add_job')
    )
    return builder.as_markup()


async def get_project_info_inline_keyboard(project_id: int, deleted: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='📷 Фотографии', callback_data=f'download_photos_project_{project_id}'))
    if deleted:
        builder.row(
            InlineKeyboardButton(text='⬆️ Опубликовать', callback_data=f'publish_project_{project_id}')
        )
    else:
        builder.row(
            InlineKeyboardButton(text='⬇️ Снять с Публикации', callback_data=f'unpublish_project_{project_id}')
        )
    builder.row(
        InlineKeyboardButton(text='✏️ Заголовок', callback_data=f'edit_project_title_{project_id}'),
        InlineKeyboardButton(text='✏️ Описание', callback_data=f'edit_project_description_{project_id}'),
    )
    builder.row(
        InlineKeyboardButton(text='✏️ Технологии', callback_data=f'edit_project_technology_{project_id}'),
        InlineKeyboardButton(text='✏️ Фото', callback_data=f'edit_project_images_{project_id}'),
    )
    return builder.as_markup()


# ================================================================= Settings Studio
async def settings_studio_inline_keyboards() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='💰 Цены', callback_data='studio_prices'),
                InlineKeyboardButton(text='👨‍👩‍👧‍👧 О команде', callback_data='studio_about_team'),
            ],
            [
                InlineKeyboardButton(text='⚙️ Тех.Поддержка', callback_data='studio_tech_support')
            ],
        ]
    )


async def settings_tech_support_inline_keyboards(exist_tech_support: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if exist_tech_support:
        builder.row(
            InlineKeyboardButton(text='👁 Показать', callback_data='show_tech_support'),
            InlineKeyboardButton(text='✏️ Изменить', callback_data='edit_tech_support'),
        )
    else:
        builder.row(
            InlineKeyboardButton(text='➕ Добавить', callback_data='add_tech_support')
        )
    return builder.as_markup()
