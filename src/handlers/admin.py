from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.filters import IsAdmin
from utils.keyboards.inline import admin as admin_inline_keyboard
from utils.keyboards.reply import admin as admin_reply_keyboard


router = Router(name='admin')


@router.message(IsAdmin(), CommandStart())
async def admin_start_command(message: Message, state: FSMContext):
    buttons = await admin_reply_keyboard.start_reply_keyboard()
    await message.answer('Hello Admin', reply_markup=buttons)
