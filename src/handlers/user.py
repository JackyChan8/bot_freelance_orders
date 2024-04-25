from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from utils.filters import IsAdmin, IsBanUser
from utils.states import user as user_states
from services import services as service_user
from utils.text import user as user_text
from utils import static_path as photo_user
from utils.pagination import pagination
from utils.keyboards.reply import user as user_reply_keyboard
from utils.keyboards.inline import user as user_inline_keyboard
from utils import utils_func


router = Router(name='users')


@router.message(~IsAdmin(), IsBanUser(), CommandStart())
async def user_start_command(message: Message, command: CommandObject, session: AsyncSession) -> None:
    """Start TG Bot Command"""
    user_id: int = message.from_user.id
    args: str = command.args

    # Added User To Database
    exist_user: bool = await service_user.check_exist_user_by_id(user_id, session)
    if not exist_user:
        await service_user.create_user(user_id, message.from_user.username, message, session)

    # Added Referral Link
    if args and args.isdigit():
        await utils_func.add_referral_link(user_id, int(args), exist_user, message, session)

    buttons = await user_reply_keyboard.start_reply_keyboard()
    logo_company: FSInputFile = FSInputFile(photo_user.COMPANY_LOGO)
    await message.answer_photo(logo_company)
    await message.answer(user_text.START_TEXT, reply_markup=buttons)


@router.message(~IsAdmin(), IsBanUser(), F.text == '👤 Профиль')
async def user_profile_command_reply(message: Message, session: AsyncSession) -> None:
    """Profile Reply Command"""
    buttons = await user_inline_keyboard.profile_inline_keyboard()
    count_orders: int = await service_user.get_count_orders_by_user_id(message.from_user.id, session)
    await message.answer(
        user_text.PROFILE_TEXT.format(
            username=message.from_user.username,
            user_id=message.from_user.id,
            count_orders=count_orders,
        ),
        reply_markup=buttons,
    )


@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'back_to_profile')
async def user_profile_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Back To Profile Inline Command"""
    await utils_func.delete_before_message(callback)
    buttons = await user_inline_keyboard.profile_inline_keyboard()
    count_orders: int = await service_user.get_count_orders_by_user_id(callback.from_user.id, session)
    await callback.message.answer(
        user_text.PROFILE_TEXT.format(
            username=callback.from_user.username,
            user_id=callback.from_user.id,
            count_orders=count_orders,
        ),
        reply_markup=buttons,
    )


# ================================================================= Order
@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'create_orders')
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


@router.callback_query(~IsAdmin(), IsBanUser(), user_states.OrderStates.order_type)
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


@router.message(~IsAdmin(), IsBanUser(), user_states.OrderStates.description, F.text.casefold() != 'отмена')
async def user_create_order_tech_task(message: Message, state: FSMContext) -> None:
    """Create Order tech task Command Reply"""
    if not message.text:
        await message.answer(**user_text.CREATE_ORDER_TEXT_DESCRIPTION_APP.as_kwargs())
        return
    buttons = await user_inline_keyboard.create_order_tech_task()
    await state.update_data(description=message.text)
    await state.set_state(user_states.OrderStates.tech_task_filename)
    await message.answer(**user_text.CREATE_ORDER_TEXT_TECH_TASK.as_kwargs(), reply_markup=buttons)


@router.callback_query(~IsAdmin(),
                       IsBanUser(),
                       user_states.OrderStates.tech_task_filename, F.data == 'web_site_tech_task_skip')
async def user_create_order_tech_task_skip(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    """"Create Order tech task skip Command Inline"""
    await state.update_data(tech_task_filename=None)
    data = await state.get_data()
    await state.clear()
    # Added To Database Order
    is_created: bool = await service_user.create_order(
        callback.from_user.id,
        **data,
        message=callback.message,
        session=session,
    )
    if is_created:
        admin_id = settings.ADMINS_ID[0]
        await utils_func.send_bot_message(callback.bot, admin_id, user_text.NOTIFY_NEW_ORDER)


@router.callback_query(~IsAdmin(),
                       IsBanUser(),
                       user_states.OrderStates.tech_task_filename, F.data == 'web_site_type_app_upload')
async def user_create_order_tech_task_upload(callback: CallbackQuery) -> None:
    """Create Order tech task upload Command Inline"""
    skip_button = await user_reply_keyboard.skip_reply_keyboard()
    await callback.message.answer(**user_text.CREATE_ORDER_TEXT_UPLOAD_TECH_TASK.as_kwargs(), reply_markup=skip_button)


@router.message(~IsAdmin(), IsBanUser(), user_states.OrderStates.tech_task_filename, F.text.casefold() == 'пропустить')
async def user_create_order_skip_task_tech_upload(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Create Order skip upload tech task Command Reply"""
    await state.update_data(tech_task_filename=None)
    data = await state.get_data()
    await state.clear()
    # Added To Database Order
    await service_user.create_order(message.from_user.id, **data, message=message, session=session)


@router.message(~IsAdmin(), IsBanUser(), user_states.OrderStates.tech_task_filename)
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


@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'my_orders')
async def user_get_my_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get My Orders Command Inline"""
    user_id: int = callback.from_user.id
    count_orders: int = await service_user.get_count_orders_by_user_id(callback.from_user.id, session)
    if count_orders:
        await utils_func.delete_before_message(callback)
        await pagination(type_='order', message=callback.message, session=session, user_id=user_id)
    else:
        await callback.message.answer(user_text.NOT_EXISTS_ORDERS)


@router.callback_query(~IsAdmin(), IsBanUser(), F.data.startswith('order_user_№'))
async def user_get_my_order(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Information Order Command Inline"""
    user_id: int = callback.from_user.id
    order_id: int = int(callback.data.split('№')[-1])
    # Get Order
    order = await service_user.get_my_order(user_id, order_id, session)
    # Output Information Order
    await utils_func.output_info_order(order_id, order, callback.message, session)


# ================================================================= Referral System

@router.message(~IsAdmin(), IsBanUser(), F.text == '💎 Ищем партнёров!')
async def user_found_partners_command_reply(message: Message) -> None:
    """Found Partners Command Reply"""
    await message.answer(
        user_text.FOUND_PARTNERS_TEXT.format(
            username=message.from_user.username,
            bot_username=settings.BOT_USERNAME,
            referral_link=message.from_user.id,
        )
    )


@router.callback_query(~IsAdmin(), IsBanUser(), (F.data == 'referral_systems') | (F.data == 'back_to_referral_history'))
async def referral_system_info(callback: CallbackQuery, session: AsyncSession) -> None:
    """Referral System Command Inline"""
    await utils_func.delete_before_message(callback)
    users = ''
    user_id: int = callback.from_user.id
    buttons = await user_inline_keyboard.referral_inline_keyboards()
    # Get Count Referral Links
    refer_count: int = await service_user.get_count_refer_link(user_id, session)
    if refer_count > 0:
        # Get Referral Users
        users = await utils_func.get_referral_users(user_id, callback, session)
    await callback.message.answer(
        user_text.REFERRAL_SYSTEM_INFO.format(count_referral=refer_count, users=users),
        reply_markup=buttons,
    )


@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'referral_history_pay')
async def referral_system_history_pay(callback: CallbackQuery) -> None:
    """Referral System History Accrual Command Inline"""
    await utils_func.delete_before_message(callback)
    count_pay = 0
    buttons = await user_inline_keyboard.referral_history_pay_keyboards()
    await callback.message.answer(
        user_text.REFERRAL_SYSTEM_HISTORY_PAY.format(count_pay=count_pay),
        reply_markup=buttons,
    )


# ================================================================= Promo Code
@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'my_promo_codes')
async def user_my_promo_codes_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get My Promo Codes Command Inline"""
    user_id: int = callback.from_user.id
    # Get Count Promo Codes
    count_promo_codes: int = await service_user.get_count_promo_codes_by_user_id(user_id, session)
    if count_promo_codes:
        await utils_func.delete_before_message(callback)
        await pagination(
            type_='promocode',
            message=callback.message,
            session=session,
            user_id=user_id,
        )
    else:
        await callback.message.answer(user_text.NOT_EXISTS_PROMO_CODES)


@router.callback_query(~IsAdmin(), IsBanUser(), F.data.startswith('promocode_user_№'))
async def user_get_my_promo_code_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Information Promo Code Command Inline"""
    user_id: int = callback.from_user.id
    promo_code_id: int = int(callback.data.split('№')[-1])
    # Get Promo Code
    promo_code = await service_user.get_my_promo_code(user_id, promo_code_id, session)
    # Output Information Promo Code
    await utils_func.output_info_promo_code(promo_code_id, promo_code, callback.message)


@router.callback_query(~IsAdmin(), IsBanUser(), F.data.startswith('apply_promo_code_'))
async def user_apply_promo_code_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Output Orders for applying Promo Code"""
    promo_code_id: int = int(callback.data.split('_')[-1])
    user_id: int = callback.from_user.id
    # Get Orders
    count_orders = await service_user.get_count_orders_by_user_id(user_id, session)
    if count_orders:
        await utils_func.delete_before_message(callback)
        await pagination(
            type_=f'promocode_order_{promo_code_id}',
            message=callback.message,
            session=session,
            user_id=user_id,
        )
    else:
        await callback.message.answer(user_text.NOT_EXISTS_ORDERS)


@router.callback_query(~IsAdmin(), IsBanUser(), F.data.startswith('promocode_order_'))
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
    # Check is Active Promo Code
    is_active = await service_user.check_is_active_promo_code(promo_code_id, session)
    if not is_active:
        await callback.message.answer(user_text.PROMO_CODE_IS_NOT_ACTIVE)
        return
    # Added to Promo Code Order ID
    await service_user.apply_promo_code(user_id, promo_code_id, order_id, callback.message, session)
    await user_profile_command_inline(callback, session)


# =================================================================


@router.message(~IsAdmin(), IsBanUser(), F.text == '💰 Цены')
async def user_costs_command_reply(message: Message) -> None:
    await message.answer('Наши Цены')


# ================================================================= About Us Menu
@router.message(~IsAdmin(), IsBanUser(), F.text == '‍💻 О нас')
async def user_about_us_command_reply(message: Message) -> None:
    """About us Reply Command"""
    buttons = await user_inline_keyboard.about_us_inline_keyboard()
    await message.answer(user_text.ABOUT_US_TEXT, reply_markup=buttons)


@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'back_to_about_us')
async def user_back_to_about_us(callback: CallbackQuery) -> None:
    await user_about_us_command_reply(callback.message)


@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'our_reviews')
async def user_our_reviews_inline(callback: CallbackQuery) -> None:
    """Review Inline Command"""
    buttons = await user_inline_keyboard.reviews_menu_inline_keyboard()
    await callback.message.answer(user_text.REVIEWS_TEXT, reply_markup=buttons)


# ================================================================= Reviews
@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'add_review')
async def user_write_review(callback: CallbackQuery, state: FSMContext) -> None:
    """Write Review Inline Command"""
    cancel_button = await user_reply_keyboard.cancel_reply_keyboard()
    await state.set_state(user_states.ReviewStates.text)
    await callback.message.answer(
        **user_text.CREATE_REVIEW_MESSAGE.as_kwargs(),
        reply_markup=cancel_button,
    )


@router.message(~IsAdmin(), IsBanUser(), user_states.ReviewStates.text, F.text.casefold() != 'отмена')
async def user_create_review_message(message: Message, state: FSMContext) -> None:
    """Write Text Review Reply Command"""
    buttons = await user_inline_keyboard.reviews_add_rating()
    await state.update_data(text=message.text)
    await state.set_state(user_states.ReviewStates.rating)
    await message.answer(**user_text.CREATE_REVIEW_RATING.as_kwargs(), reply_markup=buttons)


@router.callback_query(~IsAdmin(), IsBanUser(), user_states.ReviewStates.rating)
async def user_create_review_rating(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    """Choose Rating Review Inline Command"""
    rating: int = int(callback.data.split('_')[-1])
    await state.update_data(rating=rating)
    data = await state.get_data()
    await state.clear()
    # Added To Database Review
    await service_user.create_review(callback.from_user.id, **data, message=callback.message, session=session)


@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'show_review')
async def user_show_reviews(callback: CallbackQuery, session: AsyncSession) -> None:
    """Show reviews Inline Command"""
    user_id: int = callback.from_user.id
    reviews_count: int = await service_user.get_reviews_by_user_id(callback.from_user.id, session)
    if reviews_count:
        await utils_func.delete_before_message(callback)
        await pagination(type_='review',
                         message=callback.message,
                         callback_back='our_reviews',
                         session=session,
                         user_id=user_id)
    else:
        await callback.message.answer(user_text.NOT_EXISTS_REVIEWS)


@router.callback_query(~IsAdmin(), IsBanUser(), F.data.startswith('review_user_№'))
async def user_get_review(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Reviews"""
    review_id: int = int(callback.data.split('№')[-1])
    # Output Information Promo Code
    await utils_func.output_info_review(review_id, callback.message, session)


# ================================================================= Our Jobs
@router.callback_query(~IsAdmin(), IsBanUser(), F.data == 'our_works')
async def user_our_works_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    count_jobs: int = await service_user.get_count_projects_by_user(session=session)
    if count_jobs:
        await utils_func.delete_before_message(callback)
        await pagination(
            type_='projects',
            message=callback.message,
            callback_back='back_to_about_us',
            callback_type='user',
            session=session,
        )
    else:
        await callback.message.answer(user_text.NOT_EXISTS_JOBS)


@router.callback_query(~IsAdmin(), F.data.startswith('projects_user_№'))
async def user_get_project_info_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Project Information Command Inline"""
    await utils_func.output_info_project(callback, session, type_user='user')


# =================================================================

@router.message(~IsAdmin(), IsBanUser(), F.text == '🛠 Тех.поддержка')
async def user_support_command_reply(message: Message, session: AsyncSession) -> None:
    """Tech Support Command Reply"""
    tech_support = await service_user.get_tech_support(session)
    if tech_support:
        await message.answer(
            user_text.SUPPORT_TEXT.format(username=tech_support.username, email=tech_support.email),
        )
    else:
        await message.answer(user_text.SUPPORT_TEXT_NOT_FOUND)
