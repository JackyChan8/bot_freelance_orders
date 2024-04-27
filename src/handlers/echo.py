from aiogram.types import Message
from aiogram import Router

from utils.text.user import NOT_FOUND_COMMAND
from config import decorate_logging

router = Router(name='echo')


@router.message()
@decorate_logging
async def echo_handler(message: Message):
    await message.answer(NOT_FOUND_COMMAND)
