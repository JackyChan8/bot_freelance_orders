from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def start_inline_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text='Is Admin', callback_data='is_admin'))
    return markup.as_markup()
