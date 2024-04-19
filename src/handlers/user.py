from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from utils.filters import IsAdmin
from utils.states import user as user_states
from services import services as service_user
from utils.text import user as user_text
from utils import static_path as photo_user
from utils.pagination import pagination, Pagination, paginationTypeText
from utils.keyboards.reply import user as user_reply_keyboard
from utils.keyboards.inline import user as user_inline_keyboard

router = Router(name='users')


async def add_referral_link(user_id: int, referral_id: int, exist_user: bool, message: Message,
                            session: AsyncSession) -> None:
    """Added Referral Link"""
    if referral_id == user_id:
        await message.answer(user_text.NOT_USE_SELF_REFERRAL_LINK)
    else:
        # Check Exists User
        if exist_user:
            return
        # Add To Database Referral Link
        result = await service_user.create_refer_link(user_id, referral_id, session)
        if result:
            await message.bot.send_message(
                referral_id, user_text.SUCCESS_CREATE_BY_REFERRAL_LINK.format(username=message.from_user.username)
            )


async def get_referral_users(user_id: int, callback: CallbackQuery, session: AsyncSession) -> str:
    """Get Referral Users"""
    users = await service_user.get_referral_users_id(user_id, session)
    chat_members = [await callback.bot.get_chat_member(user, user) for user in users]
    return '\n'.join([f'@{member.user.username}' for member in chat_members])


async def delete_before_message(callback: CallbackQuery) -> None:
    """Delete Before Message"""
    await callback.message.delete()


@router.message(~IsAdmin(), CommandStart())
async def user_start_command(message: Message, command: CommandObject, session: AsyncSession) -> None:
    """Start TG Bot Command"""
    user_id: int = message.from_user.id
    args: str = command.args

    # Added User To Database
    exist_user: bool = await service_user.check_exist_user(user_id, session)
    if not exist_user:
        await service_user.create_user(user_id, message.from_user.username, message, session)

    # Added Referral Link
    if args and args.isdigit():
        await add_referral_link(user_id, int(args), exist_user, message, session)

    buttons = await user_reply_keyboard.start_reply_keyboard()
    logo_company: FSInputFile = FSInputFile(photo_user.COMPANY_LOGO)
    await message.answer_photo(logo_company)
    await message.answer(user_text.START_TEXT, reply_markup=buttons)


@router.message(~IsAdmin(), F.text == '👤 Профиль')
async def user_profile_command_reply(message: Message, session: AsyncSession) -> None:
    """Profile Reply Command"""
    buttons = await user_inline_keyboard.profile_inline_keyboard()
    count_orders: int = await service_user.get_count_orders(message.from_user.id, session)
    await message.answer(
        user_text.PROFILE_TEXT.format(
            username=message.from_user.username,
            user_id=message.from_user.id,
            count_orders=count_orders,
        ),
        reply_markup=buttons,
    )


@router.callback_query(~IsAdmin(), F.data == 'back_to_profile')
async def user_profile_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Back To Profile Inline Command"""
    await delete_before_message(callback)
    buttons = await user_inline_keyboard.profile_inline_keyboard()
    count_orders: int = await service_user.get_count_orders(callback.from_user.id, session)
    await callback.message.answer(
        user_text.PROFILE_TEXT.format(
            username=callback.from_user.username,
            user_id=callback.from_user.id,
            count_orders=count_orders,
        ),
        reply_markup=buttons,
    )


# ================================================================= Order
@router.callback_query(~IsAdmin(), F.data == 'create_orders')
async def user_create_order_type_app(callback: CallbackQuery, state: FSMContext) -> None:
    """Create Order type application Command Inline"""
    buttons = await user_inline_keyboard.create_order_type_app()
    cancel_button = await user_reply_keyboard.cancel_reply_keyboard()

    await state.set_state(user_states.OrderStates.order_type)
    await callback.message.answer(
        text=user_text.CREATE_ORDER_TEXT_INFO.format(username=callback.from_user.username),
        reply_markup=cancel_button,
    )
    await callback.message.answer(**user_text.CREATE_ORDER_TEXT_TYPE_APP.as_kwargs(), reply_markup=buttons)


@router.callback_query(~IsAdmin(), user_states.OrderStates.order_type)
async def user_create_order_description(callback: CallbackQuery, state: FSMContext) -> None:
    """Create Order description Command Inline"""
    type_app: dict = {
        'web_site_type_app': 'Веб-Сайт',
        'telegram_bot_type_app': 'Telegram Bot',
        'server_type_app': 'Работа с серверами',
        'layout_type_app': 'Верстка',
        'script_type_app': 'Скрипт',
    }

    await state.update_data(order_type=type_app.get(callback.data))
    await state.set_state(user_states.OrderStates.description)
    await callback.message.answer(
        **user_text.CREATE_ORDER_TEXT_DESCRIPTION_APP.as_kwargs()
    )


@router.message(~IsAdmin(), user_states.OrderStates.description, F.text.casefold() != 'отмена')
async def user_create_order_tech_task(message: Message, state: FSMContext) -> None:
    """Create Order tech task Command Reply"""
    if not message.text:
        await message.answer(**user_text.CREATE_ORDER_TEXT_DESCRIPTION_APP.as_kwargs())
        return
    buttons = await user_inline_keyboard.create_order_tech_task()
    await state.update_data(description=message.text)
    await state.set_state(user_states.OrderStates.tech_task_filename)
    await message.answer(**user_text.CREATE_ORDER_TEXT_TECH_TASK.as_kwargs(), reply_markup=buttons)


@router.callback_query(~IsAdmin(), user_states.OrderStates.tech_task_filename, F.data == 'web_site_tech_task_skip')
async def user_create_order_tech_task_skip(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    """"Create Order tech task skip Command Inline"""
    await state.update_data(tech_task_filename=None)
    data = await state.get_data()
    await state.clear()
    # Added To Database Order
    await service_user.create_order(callback.from_user.id, **data, message=callback.message, session=session)


@router.callback_query(~IsAdmin(), user_states.OrderStates.tech_task_filename, F.data == 'web_site_type_app_upload')
async def user_create_order_tech_task_upload(callback: CallbackQuery) -> None:
    """Create Order tech task upload Command Inline"""
    skip_button = await user_reply_keyboard.skip_reply_keyboard()
    await callback.message.answer(**user_text.CREATE_ORDER_TEXT_UPLOAD_TECH_TASK.as_kwargs(), reply_markup=skip_button)


@router.message(~IsAdmin(), user_states.OrderStates.tech_task_filename, F.text.casefold() == 'пропустить')
async def user_create_order_skip_task_tech_upload(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Create Order skip upload tech task Command Reply"""
    await state.update_data(tech_task_filename=None)
    data = await state.get_data()
    await state.clear()
    # Added To Database Order
    await service_user.create_order(message.from_user.id, **data, message=message, session=session)


@router.message(~IsAdmin(), user_states.OrderStates.tech_task_filename)
async def user_create_order_tech_task_upload_finish(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Create Order upload tech task Command Reply"""
    if not message.document:
        await message.answer(**user_text.CREATE_ORDER_TEXT_UPLOAD_TECH_TASK.as_kwargs())
        return
    # Download File
    file_id: str = message.document.file_id
    file_name: str = message.date.now().strftime('%m_%d_%Y_%H_%M_%S') + message.document.file_name
    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, photo_user.ORDERS_FILES + file_name)
    # Added To Database Order
    await state.update_data(tech_task_filename=file_name)
    data = await state.get_data()
    await state.clear()
    await service_user.create_order(message.from_user.id, **data, message=message, session=session)


@router.callback_query(~IsAdmin(), F.data == 'my_orders')
async def user_get_my_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get My Orders Command Inline"""
    orders = await service_user.get_my_orders(callback.from_user.id, session)
    if orders:
        await delete_before_message(callback)
        await pagination(data=orders, type_='order', message=callback.message)
    else:
        await callback.message.answer(user_text.NOT_EXISTS_ORDERS)


@router.callback_query(~IsAdmin(), F.data.startswith('order_user_№'))
async def user_get_my_order(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Information Order Command Inline"""
    user_id: int = callback.from_user.id
    order_id: int = int(callback.data.split('№')[-1])
    # Get Order
    order = await service_user.get_my_order(user_id, order_id, session)
    # Get Discount Promo Code to Order
    discount = await service_user.get_promo_code_for_order(order_id, session)
    # Generate Text
    text: str = await user_text.show_info_order(
        order_id,
        order.type,
        order.status,
        order.description,
        order.created_at,
        discount,
    )
    # Attach File Tech Task
    buttons = None
    if order.tech_task_filename:
        buttons = await user_inline_keyboard.get_tech_task_inline_keyboard(order_id)
    await callback.message.answer(text, reply_markup=buttons, parse_mode=ParseMode.HTML)


# ================================================================= Referral System

@router.message(~IsAdmin(), F.text == '💎 Ищем партнёров!')
async def user_found_partners_command_reply(message: Message) -> None:
    """Found Partners Command Reply"""
    await message.answer(
        user_text.FOUND_PARTNERS_TEXT.format(
            username=message.from_user.username,
            bot_username=settings.BOT_USERNAME,
            referral_link=message.from_user.id,
        )
    )


@router.callback_query(~IsAdmin(), (F.data == 'referral_systems') | (F.data == 'back_to_referral_history'))
async def referral_system_info(callback: CallbackQuery, session: AsyncSession) -> None:
    """Referral System Command Inline"""
    await delete_before_message(callback)
    users = ''
    user_id: int = callback.from_user.id
    buttons = await user_inline_keyboard.referral_inline_keyboards()
    # Get Count Referral Links
    refer_count: int = await service_user.get_count_refer_link(user_id, session)
    if refer_count > 0:
        # Get Referral Users
        users = await get_referral_users(user_id, callback, session)
    await callback.message.answer(
        user_text.REFERRAL_SYSTEM_INFO.format(count_referral=refer_count, users=users),
        reply_markup=buttons,
    )


@router.callback_query(~IsAdmin(), F.data == 'referral_history_pay')
async def referral_system_history_pay(callback: CallbackQuery) -> None:
    """Referral System History Accrual Command Inline"""
    await delete_before_message(callback)
    count_pay = 0
    buttons = await user_inline_keyboard.referral_history_pay_keyboards()
    await callback.message.answer(
        user_text.REFERRAL_SYSTEM_HISTORY_PAY.format(count_pay=count_pay),
        reply_markup=buttons,
    )


# ================================================================= Promo Code
@router.callback_query(~IsAdmin(), F.data == 'my_promo_codes')
async def user_my_promo_codes_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get My Promo Codes Command Inline"""
    user_id: int = callback.from_user.id
    # Get Promo Codes
    promo_codes = await service_user.get_promo_codes(user_id, session)
    if promo_codes:
        await delete_before_message(callback)
        await pagination(data=promo_codes, type_='promocode', message=callback.message)
    else:
        await callback.message.answer(user_text.NOT_EXISTS_PROMO_CODES)


@router.callback_query(~IsAdmin(), F.data.startswith('promocode_user_№'))
async def user_get_my_promo_code_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Information Order Command Inline"""
    user_id: int = callback.from_user.id
    promo_code_id: int = int(callback.data.split('№')[-1])
    # Get Promo Code
    promo_code = await service_user.get_my_promo_code(user_id, promo_code_id, session)
    # Generate text
    text: str = await user_text.show_info_promo_code(
        promo_code_id, promo_code.discount, promo_code.created_at
    )
    buttons = await user_inline_keyboard.apply_promo_code_inline_keyboard(promo_code_id)
    await callback.message.answer(text, reply_markup=buttons, parse_mode=ParseMode.HTML)


@router.callback_query(~IsAdmin(), F.data.startswith('apply_promo_code_'))
async def user_apply_promo_code_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Output Orders for applying Promo Code"""
    promo_code_id: int = int(callback.data.split('_')[-1])
    # Get Orders
    orders = await service_user.get_my_orders(callback.from_user.id, session)
    if orders:
        await delete_before_message(callback)
        await pagination(data=orders, type_=f'promocode_order_{promo_code_id}', message=callback.message)
    else:
        await callback.message.answer(user_text.NOT_EXISTS_ORDERS)


@router.callback_query(~IsAdmin(), F.data.startswith('promocode_order_'))
async def user_promo_code_choose_order(callback: CallbackQuery, session: AsyncSession) -> None:
    """Choose Order for applying Promo Code"""
    data = callback.data.split('_')
    user_id: int = callback.from_user.id
    promo_code_id: int = int(data[2])
    order_id: int = int(data[-1][1:])
    # Check Exists Promo Code Apply Order
    exist_promo_code = await service_user.check_exists_promo_code_order(user_id, order_id, session)
    if exist_promo_code:
        await callback.message.answer(user_text.PROMO_CODE_EXIST_ORDER)
        return
    # Added to Promo Code Order ID
    await service_user.apply_promo_code(user_id, promo_code_id, order_id, callback.message, session)
    await user_profile_command_inline(callback, session)


# ================================================================= Navigation


@router.callback_query(~IsAdmin(), Pagination.filter())
async def pagination_handler(callback: CallbackQuery, callback_data: Pagination, session: AsyncSession) -> None:
    """Pagination Handler"""
    await delete_before_message(callback)
    page: int = callback_data.page
    type_: str = callback_data.type
    # Get Data for pagination
    type_text: tuple = paginationTypeText.get(type_, paginationTypeText.get('order'))
    data = await type_text[1](callback.from_user.id, session)
    callback_data: str = type_text[2]
    await pagination(data=data, type_=type_, message=callback.message, page=page, callback_back=callback_data)


# =================================================================


@router.message(~IsAdmin(), F.text == '💰 Цены')
async def user_costs_command_reply(message: Message) -> None:
    await message.answer('Наши Цены')


# ================================================================= About Us Menu
@router.message(~IsAdmin(), F.text == '‍💻 О нас')
async def user_about_us_command_reply(message: Message) -> None:
    """About us Reply Command"""
    buttons = await user_inline_keyboard.about_us_inline_keyboard()
    await message.answer(user_text.ABOUT_US_TEXT, reply_markup=buttons)


@router.callback_query(~IsAdmin(), F.data == 'our_reviews')
async def user_our_reviews_inline(callback: CallbackQuery) -> None:
    """Review Inline Command"""
    buttons = await user_inline_keyboard.reviews_menu_inline_keyboard()
    await callback.message.answer(user_text.REVIEWS_TEXT, reply_markup=buttons)


# ================================================================= Reviews
@router.callback_query(~IsAdmin(), F.data == 'add_review')
async def user_write_review(callback: CallbackQuery, state: FSMContext) -> None:
    """Write Review Inline Command"""
    cancel_button = await user_reply_keyboard.cancel_reply_keyboard()
    await state.set_state(user_states.ReviewStates.text)
    await callback.message.answer(
        **user_text.CREATE_REVIEW_MESSAGE.as_kwargs(),
        reply_markup=cancel_button,
    )


@router.message(~IsAdmin(), user_states.ReviewStates.text, F.text.casefold() != 'отмена')
async def user_create_review_message(message: Message, state: FSMContext) -> None:
    """Write Text Review Reply Command"""
    buttons = await user_inline_keyboard.reviews_add_rating()
    await state.update_data(text=message.text)
    await state.set_state(user_states.ReviewStates.rating)
    await message.answer(**user_text.CREATE_REVIEW_RATING.as_kwargs(), reply_markup=buttons)


@router.callback_query(~IsAdmin(), user_states.ReviewStates.rating)
async def user_create_review_rating(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    """Choose Rating Review Inline Command"""
    rating: int = int(callback.data.split('_')[-1])
    await state.update_data(rating=rating)
    data = await state.get_data()
    await state.clear()
    # Added To Database Review
    await service_user.create_review(callback.from_user.id, **data, message=callback.message, session=session)


@router.callback_query(~IsAdmin(), F.data == 'show_review')
async def user_show_reviews(callback: CallbackQuery, session: AsyncSession) -> None:
    """Show reviews"""
    reviews = await service_user.get_reviews(callback.from_user.id, session)
    if reviews:
        await delete_before_message(callback)
        await pagination(data=reviews, type_='review', message=callback.message, callback_back='our_reviews')
    else:
        await callback.message.answer(user_text.NOT_EXISTS_REVIEWS)


@router.callback_query(~IsAdmin(), F.data.startswith('review_user_№'))
async def user_get_review(callback: CallbackQuery, session: AsyncSession) -> None:
    print('user_get_review')
    review_id: int = int(callback.data.split('№')[-1])
    # Get Review
    review = await service_user.get_review(review_id, session)
    # Get Author Review Username
    review_author = await callback.bot.get_chat_member(review.author, review.author)
    # Generate Text
    text: str = await user_text.show_info_review(
        review_id, review_author.user.username, review.message, review.rating, review.created_at)
    await callback.message.answer(text, parse_mode=ParseMode.HTML)


# =================================================================

@router.message(~IsAdmin(), F.text == '📋 Правила')
async def user_rules_command_reply(message: Message) -> None:
    await message.answer('Правила нашей студии')


@router.message(~IsAdmin(), F.text == '🛠 Тех.поддержка')
async def user_support_command_reply(message: Message) -> None:
    await message.answer(user_text.SUPPORT_TEXT)
