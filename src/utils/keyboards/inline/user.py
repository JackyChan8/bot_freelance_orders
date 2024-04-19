from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def profile_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Мои Заказы', callback_data='my_orders')],
            [InlineKeyboardButton(text='Создать Заказ', callback_data='create_orders')],
            [InlineKeyboardButton(text='Мои промокоды', callback_data='my_promo_codes')],
            [InlineKeyboardButton(text='Реферальная система', callback_data='referral_systems')],
        ]
    )


# ================================================================= Order


async def create_order_type_app() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Веб-Сайт', callback_data='web_site_type_app'),
                InlineKeyboardButton(text='Telegram Bot', callback_data='telegram_bot_type_app'),
            ],
            [
                InlineKeyboardButton(text='Работа с серверами', callback_data='server_type_app'),
                InlineKeyboardButton(text='Верстка', callback_data='layout_type_app'),
            ],
            [
                InlineKeyboardButton(text='Скрипт', callback_data='script_type_app'),
            ]
        ]
    )


async def create_order_tech_task() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Приложить', callback_data='web_site_type_app_upload'),
                InlineKeyboardButton(text='Пропустить', callback_data='web_site_tech_task_skip'),
            ]
        ]
    )


async def get_tech_task_inline_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📥 Скачать Техн.Задание', callback_data=f'download_file_order_{order_id}')]
        ]
    )

# ================================================================= Referral System


async def referral_inline_keyboards() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='История начислений', callback_data='referral_history_pay')],
            [InlineKeyboardButton(text='« Назад', callback_data='back_to_profile')],
        ]
    )


async def referral_history_pay_keyboards() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='« Назад', callback_data='back_to_referral_history')],
        ]
    )


# ================================================================= Promo Code
async def apply_promo_code_inline_keyboard(promo_code_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📮 Применить Промокод', callback_data=f'apply_promo_code_{promo_code_id}')]
        ]
    )

# =================================================================


async def about_us_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Наши Работы', callback_data='our_works')],
            [InlineKeyboardButton(text='Наш Сайт', url='https://google.com/')],
            [InlineKeyboardButton(text='Отзывы', callback_data='our_reviews')],
            [InlineKeyboardButton(text='О команде', callback_data='our_team')],
        ]
    )


async def reviews_menu_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Оставить Отзыв', callback_data='add_review')],
            [InlineKeyboardButton(text='Показать Отзывы', callback_data='show_review')],
        ],
    )
