from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def start_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📦 Заказы')],
            [KeyboardButton(text='🎟 Промокоды'), KeyboardButton(text='👤 Пользователи')],
            [KeyboardButton(text='#️⃣ Отзывы')],
            [KeyboardButton(text='🛠 Настройка')]
        ]
    )
