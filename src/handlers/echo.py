from aiogram.types import Message
from aiogram import Router

from utils.text.user import NOT_FOUND_COMMAND

router = Router(name='echo')


@router.message()
async def echo_handler(message: Message):
    await message.answer(NOT_FOUND_COMMAND)
