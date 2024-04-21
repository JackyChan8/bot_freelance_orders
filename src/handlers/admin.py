from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from services import services as service_admin
from utils import utils_func
from utils.filters import IsAdmin
from utils.text import admin as admin_text
from utils.keyboards.reply import user as user_reply_keyboard
from utils.keyboards.inline import admin as admin_inline_keyboard
from utils.keyboards.reply import admin as admin_reply_keyboard
from utils.pagination import pagination
from utils.states import admin as admin_states

router = Router(name='admin')


@router.message(IsAdmin(), CommandStart())
async def admin_start_command(message: Message) -> None:
    buttons = await admin_reply_keyboard.start_reply_keyboard()
    await message.answer(admin_text.START_TEXT, reply_markup=buttons)


@router.callback_query(IsAdmin(), F.data == 'back_to_main_menu')
async def admin_back_command_inline(callback: CallbackQuery) -> None:
    await admin_start_command(callback.message)


# ================================================================= Orders

@router.message(IsAdmin(), F.text == '📦 Заказы')
async def admin_orders_command_reply(message: Message, session: AsyncSession) -> None:
    buttons = await admin_inline_keyboard.orders_inline_keyboard()
    # Get Count Orders By Status
    total, new, coordination, work, test, finish = await service_admin.get_count_by_status(session)
    await message.answer(
        admin_text.ORDERS_TEXT.format(
            total_orders=total,
            total_new_orders=new,
            total_coord_orders=coordination,
            total_work_orders=work,
            total_test_orders=test,
            total_finish_orders=finish,
        ),
        reply_markup=buttons,
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(IsAdmin(), F.data == 'back_to_orders')
async def admin_orders_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    await utils_func.delete_before_message(callback)
    await admin_orders_command_reply(callback.message, session)


@router.callback_query(IsAdmin(), F.data.endswith('_show_orders'))
async def admin_show_orders_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    status: str = callback.data.split('_')[0]
    orders = await service_admin.get_orders_by_status(status, session)
    if orders:
        await utils_func.delete_before_message(callback)
        await pagination(
            data=orders,
            type_='order',
            message=callback.message,
            callback_back='back_to_orders',
            callback_type='admin',
            status=status,
        )
    else:
        await callback.message.answer(admin_text.NOT_EXISTS_ORDERS_WITH_STATUS)


@router.callback_query(IsAdmin(), F.data.startswith('order_admin_№'))
async def admin_get_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    order_id: int = int(callback.data.split('№')[-1])
    # Get Order
    order = await service_admin.get_order(order_id, session)
    # Output Information Order
    await utils_func.output_info_order(order_id, order, callback.message, session, is_admin=True)


@router.callback_query(IsAdmin(), F.data.startswith('change_status_order_'))
async def admin_change_status_order_choose(callback: CallbackQuery) -> None:
    """Change Status Order, Choose Status"""
    order_id: int = int(callback.data.split('_')[-1])
    buttons = await admin_inline_keyboard.orders_inline_keyboard(order_id)
    await callback.message.answer(admin_text.CHANGE_STATUS_ORDER_TEXT, reply_markup=buttons)


@router.callback_query(IsAdmin(), F.data.contains('save_choose_status'))
async def admin_change_status_order(callback: CallbackQuery, session: AsyncSession) -> None:
    """Change Status Order, Save"""
    data: list = callback.data.split('_')
    status: str = data[0]
    order_id: int = int(data[-1])
    # Check Status Order
    status_order = await service_admin.get_order_status(order_id, session)
    if status_order == utils_func.statuses.get(status):
        await callback.message.answer(admin_text.NOT_CHANGE_EXISTS_STATUS)
        return
    # Change Status Order
    is_changed: bool = await service_admin.change_status_order(order_id, status, callback.message, session)
    if is_changed:
        # Get Customer ID And Send Notification
        customer_id, _ = await service_admin.get_customer_by_order(order_id, session)
        text = await admin_text.notify_success_change_order(order_id, status)
        await utils_func.send_bot_message(callback.bot, customer_id, text)


@router.callback_query(IsAdmin(), F.data.startswith('show_customer_order_'))
async def admin_show_customer_order(callback: CallbackQuery, session: AsyncSession) -> None:
    """Show Customer Order"""
    order_id: int = int(callback.data.split('_')[-1])
    customer = await service_admin.get_customer_by_order(order_id, session)
    if customer:
        await callback.message.answer(f'@{customer[1]}')


# ================================================================= Promo Codes
@router.message(IsAdmin(), F.text == '🎟 Промокоды')
async def admin_promo_code_command_reply(message: Message) -> None:
    """Promo Code Menu Reply Command"""
    buttons = await admin_inline_keyboard.promo_code_inline_keyboards()
    await message.answer(admin_text.PROMO_CODE_MENU_TEXT, reply_markup=buttons)


@router.callback_query(IsAdmin(), F.data == 'back_to_promo_code')
async def admin_promo_code_command_inline(callback: CallbackQuery) -> None:
    """Promo Code Menu Inline Command"""
    buttons = await admin_inline_keyboard.promo_code_inline_keyboards()
    await callback.message.answer(admin_text.PROMO_CODE_MENU_TEXT, reply_markup=buttons)


@router.callback_query(IsAdmin(), F.data == 'create_promo_code')
async def admin_create_promo_code_inline_keyboard(callback: CallbackQuery, state: FSMContext) -> None:
    """Create Promo Code Inline Keyboard"""
    cancel_button = await user_reply_keyboard.cancel_reply_keyboard()

    await state.set_state(admin_states.PromoCodeStates.username)
    await callback.message.answer(
        **admin_text.SET_USERNAME_PROMO_CODE_TEXT.as_kwargs(),
        reply_markup=cancel_button,
    )


@router.message(IsAdmin(), admin_states.PromoCodeStates.username, F.text.casefold() != 'отмена')
async def admin_create_promo_code_username(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Create Promo Code - Set username"""
    if not message.text:
        await message.answer(**admin_text.SET_USERNAME_PROMO_CODE_TEXT.as_kwargs())
        return
    # Check User Exists
    exist_user: bool = await service_admin.check_exist_user_by_username(message.text, session)
    if not exist_user:
        await message.answer(admin_text.NOT_FOUND_USERNAME_PROMO_CODE_TEXT)
        return

    await state.update_data(username=message.text)
    await state.set_state(admin_states.PromoCodeStates.discount)
    await message.answer(**admin_text.SET_DISCOUNT_PROMO_CODE_TEXT.as_kwargs())


@router.message(IsAdmin(), admin_states.PromoCodeStates.discount)
async def admin_create_promo_code_username(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Create Promo Code - Set Discount"""
    if not message.text or not message.text.isdigit():
        await message.answer(**admin_text.SET_DISCOUNT_PROMO_CODE_TEXT.as_kwargs())
        return
    discount: int = int(message.text)

    # Check Valid Discount
    if 0 >= discount or discount > 100:
        await message.answer(admin_text.SET_DISCOUNT_PROMO_CODE_RANGE)
        return

    await state.update_data(discount=discount)
    data: dict = await state.get_data()
    await state.clear()

    # Add To Database Promo Code
    user_id: int = await service_admin.get_user_id_by_username(data.get('username'), session)
    is_created: bool = await service_admin.create_promo_code(user_id, discount, message, session)
    if is_created:
        await message.bot.send_message(user_id, admin_text.NOTIFY_PROMO_CODE_SUCCESS_ADD.format(discount=discount))
        await admin_start_command(message)


@router.callback_query(IsAdmin(), F.data == 'show_promo_code')
async def admin_show_promo_code_inline_keyboard(callback: CallbackQuery, session: AsyncSession) -> None:
    """Show Promo Code Inline Keyboard"""
    # Get Promo Codes
    promo_codes = await service_admin.get_promo_codes(session=session)
    if promo_codes:
        await utils_func.delete_before_message(callback)
        await pagination(
            data=promo_codes,
            type_='promocode',
            message=callback.message,
            callback_back='back_to_promo_code',
            callback_type='admin',
        )
    else:
        await callback.message.answer(admin_text.NOT_EXISTS_PROMO_CODES)


@router.callback_query(IsAdmin(), F.data.startswith('promocode_admin_№'))
async def admin_get_promo_code(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Information Promo Code Command Inline"""
    promo_code_id: int = int(callback.data.split('№')[-1])
    # Get Promo code
    promo_code = await service_admin.get_promo_code_by_id(promo_code_id, session)
    # Output Information Promo Code
    await utils_func.output_info_promo_code(promo_code_id, promo_code, callback.message, is_admin=True)


@router.callback_query(IsAdmin(), F.data.startswith('delete_promo_code'))
async def admin_delete_promo_code(callback: CallbackQuery, session: AsyncSession) -> None:
    """Delete Promo code Command Inline"""
    promo_code_id: int = int(callback.data.split('_')[-1])
    await service_admin.delete_promo_code(promo_code_id, callback.message, session)


@router.callback_query(IsAdmin(), F.data.startswith('show_promo_code_user'))
async def admin_show_user_promo_code(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get the Owner of the Promo Code Command Inline"""
    promo_code_id: int = int(callback.data.split('_')[-1])
    customer = await service_admin.get_owner_promo_code(promo_code_id, session)
    if customer:
        await callback.message.answer(f'@{customer[1]}')


# ================================================================= Users
@router.message(IsAdmin(), F.text == '👤 Пользователи')
async def admin_users_command_reply(message: Message, session: AsyncSession) -> None:
    """Users Menu Reply Command"""
    pass


# ================================================================= Reviews
@router.message(IsAdmin(), F.text == '#️⃣ Отзывы')
async def admin_reviews_command_reply(message: Message) -> None:
    """Reviews Menu Reply Command"""
    buttons = await admin_inline_keyboard.reviews_inline_keyboards()
    await message.answer(admin_text.REVIEWS_MENU_TEXT, reply_markup=buttons)


@router.callback_query(IsAdmin(), F.data == 'back_to_reviews')
async def admin_reviews_command_inline(callback: CallbackQuery) -> None:
    """Reviews Menu Inline Command"""
    buttons = await admin_inline_keyboard.reviews_inline_keyboards()
    await callback.message.answer(admin_text.REVIEWS_MENU_TEXT, reply_markup=buttons)


@router.callback_query(IsAdmin(), F.data == 'show_reviews')
async def admin_show_reviews_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Show Reviews Inline Command"""
    reviews = await service_admin.get_reviews(session=session)
    if reviews:
        await utils_func.delete_before_message(callback)
        await pagination(
            data=reviews,
            type_='review',
            message=callback.message,
            callback_back='back_to_reviews',
            callback_type='admin',
        )
    else:
        await callback.message.answer(admin_text.NOT_EXISTS_REVIEWS)


@router.callback_query(IsAdmin(), F.data.startswith('review_admin_№'))
async def admin_get_review(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Review Command Inline"""
    review_id: int = int(callback.data.split('№')[-1])
    # Output Information Promo Code
    await utils_func.output_info_review(review_id, callback.message, session, is_admin=True)


@router.callback_query(IsAdmin(), F.data.startswith('remove_public_review_'))
async def admin_remove_from_publish_review_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Remove From Publication Review Command Inline"""
    review_id: int = int(callback.data.split('_')[-1])
    await service_admin.update_review_by_id(review_id, False, callback.message, session)


@router.callback_query(IsAdmin(), F.data.startswith('add_public_review_'))
async def admin_publish_review_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Publication Review Command Inline"""
    review_id: int = int(callback.data.split('_')[-1])
    await service_admin.update_review_by_id(review_id, True, callback.message, session)
