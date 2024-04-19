from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.keyboards.reply import user as user_reply_keyboard
from utils.filters import IsAdmin

router = Router(name='cancel')


@router.message(~IsAdmin(), F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    buttons = await user_reply_keyboard.start_reply_keyboard()
    await state.clear()
    await message.answer(
        "Операция отменена.",
        reply_markup=buttons,
    )
