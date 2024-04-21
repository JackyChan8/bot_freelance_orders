from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def start_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='👤 Профиль')],
            [KeyboardButton(text='💎 Ищем партнёров!')],
            [KeyboardButton(text='💰 Цены'), KeyboardButton(text='‍💻 О нас')],
            [KeyboardButton(text='🛠 Тех.поддержка')]
        ],
        resize_keyboard=True)


async def cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отмена')]
        ]
    )


async def skip_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Пропустить')]
        ]
    )
