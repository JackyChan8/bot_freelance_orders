from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.keyboards.reply import admin as admin_reply_keyboard
from utils.keyboards.reply import user as user_reply_keyboard
from config import settings, decorate_logging

router = Router(name='cancel')


@router.message(F.text.casefold() == 'отмена')
@decorate_logging
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if message.from_user.id in settings.ADMINS_ID:
        buttons = await admin_reply_keyboard.start_reply_keyboard()
    else:
        buttons = await user_reply_keyboard.start_reply_keyboard()
    await state.clear()
    await message.answer(
        "Операция отменена.",
        reply_markup=buttons,
    )
