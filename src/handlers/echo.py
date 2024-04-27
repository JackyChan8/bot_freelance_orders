from aiogram.types import Message
from aiogram import Router

from src.utils.text.user import NOT_FOUND_COMMAND
from src.config import decorate_logging

router = Router(name='echo')


@router.message()
@decorate_logging
async def echo_handler(message: Message):
    await message.answer(NOT_FOUND_COMMAND)
