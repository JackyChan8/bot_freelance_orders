from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

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
    count_orders: int = await service_admin.get_count_orders_by_status(status, session)
    if count_orders:
        await utils_func.delete_before_message(callback)
        await pagination(
            type_='order',
            message=callback.message,
            callback_back='back_to_orders',
            callback_type='admin',
            status=status,
            session=session,
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
    count_promo_codes: int = await service_admin.get_count_promo_codes(session=session)
    if count_promo_codes:
        await utils_func.delete_before_message(callback)
        await pagination(
            type_='promocode',
            message=callback.message,
            callback_back='back_to_promo_code',
            callback_type='admin',
            session=session,
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
    count_users: int = await service_admin.get_count_users(session=session)
    buttons = await admin_inline_keyboard.users_inline_keyboards() if count_users else None
    await message.answer(
        admin_text.USER_MENU_TEXT.format(count_users=count_users),
        reply_markup=buttons,
    )


@router.callback_query(IsAdmin(), F.data == 'back_to_users')
async def admin_users_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Users Menu Inline Command"""
    await admin_users_command_reply(callback.message, session)


@router.callback_query(IsAdmin(), F.data == 'show_users')
async def show_users_command_inline(callback: CallbackQuery, session: AsyncSession):
    """Get Users Command Inline"""
    count_users: int = await service_admin.get_count_users(session=session)
    if count_users:
        await utils_func.delete_before_message(callback)
        await pagination(
            type_='users',
            message=callback.message,
            callback_back='back_to_users',
            callback_type='admin',
            session=session,
        )
    else:
        await callback.message.answer(admin_text.NOT_EXISTS_USERS)


@router.callback_query(IsAdmin(), F.data.startswith('users_admin_№'))
async def get_user_info_command_inline(callback: CallbackQuery, session: AsyncSession):
    """Get Information User Command Inline"""
    user_id: int = int(callback.data.split('№')[-1])
    # Get User
    user: tuple = await service_admin.get_user_info(user_id, session)
    # Output Information User
    buttons = await admin_inline_keyboard.get_user_info_inline_keyboard(user_id, user[1])
    await callback.message.answer(
        admin_text.USER_INFO_TEXT.format(
            username=user[0],
            count_orders=user[2],
            count_reviews=user[3],
            count_referrals=user[4],
            count_promo_codes=user[5],
        ),
        reply_markup=buttons,
    )


@router.callback_query(IsAdmin(), F.data.startswith('unblock_user'))
async def unblock_user_command_inline(callback: CallbackQuery, session: AsyncSession):
    """Unblock User Command Inline"""
    user_id: int = int(callback.data.split('_')[-1])
    # Un Block User
    is_un_block = await service_admin.block_user(user_id, False, callback.message, session)
    if is_un_block:
        await utils_func.delete_before_message(callback)
        # Send Notification
        await utils_func.send_bot_message(callback.bot, user_id, admin_text.USER_UN_BLOCK)


@router.callback_query(IsAdmin(), F.data.startswith('block_user'))
async def block_user_command_inline(callback: CallbackQuery, session: AsyncSession):
    """Block User Command Inline"""
    user_id: int = int(callback.data.split('_')[-1])
    # Block User
    is_block = await service_admin.block_user(user_id, True, callback.message, session)
    if is_block:
        await utils_func.delete_before_message(callback)
        # Send Notification
        await utils_func.send_bot_message(callback.bot, user_id, admin_text.USER_BLOCK)


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
    count_reviews = await service_admin.get_count_reviews(session=session)
    if count_reviews:
        await utils_func.delete_before_message(callback)
        await pagination(
            type_='review',
            message=callback.message,
            callback_back='back_to_reviews',
            callback_type='admin',
            session=session,
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


# ================================================================= Settings
@router.message(IsAdmin(), F.text == '🛠 Настройка')
async def admin_settings_command_reply(message: Message) -> None:
    """Settings Menu Reply Command"""
    buttons = await admin_inline_keyboard.settings_inline_keyboards()
    await message.answer(
        admin_text.SETTINGS_MENU_TEXT,
        reply_markup=buttons,
    )


@router.callback_query(IsAdmin(), F.data == 'back_to_settings')
async def admin_settings_command_inline(callback: CallbackQuery) -> None:
    """Settings Menu Inline Command"""
    buttons = await admin_inline_keyboard.settings_inline_keyboards()
    await callback.message.answer(
        admin_text.SETTINGS_MENU_TEXT,
        reply_markup=buttons,
    )


# ================================================================= Our Jobs

@router.callback_query(IsAdmin(), F.data == 'our_jobs')
async def admin_tech_support_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Our Project Menu Inline Command"""
    # Check Exists Project
    exists_jobs = await service_admin.check_exists_projects(session)
    buttons = await admin_inline_keyboard.add_our_works(exists_jobs)
    await callback.message.answer(admin_text.SETTINGS_MENU_TEXT, reply_markup=buttons)


@router.callback_query(IsAdmin(), F.data == 'add_job')
async def admin_add_project_command_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """Create Project Command Inline"""
    cancel_button = await user_reply_keyboard.cancel_reply_keyboard()

    await state.set_state(admin_states.JobStates.title)
    await callback.message.answer(
        **admin_text.JOBS_TITLE_TEXT.as_kwargs(),
        reply_markup=cancel_button,
    )


@router.message(IsAdmin(), admin_states.JobStates.title, F.text.casefold() != 'отмена')
async def admin_add_project_title(message: Message, state: FSMContext) -> None:
    """Create Project title Command Reply"""
    await state.update_data(title=message.text)
    await state.set_state(admin_states.JobStates.description)
    await message.answer(**admin_text.JOBS_TITLE_DESCRIPTION.as_kwargs())


@router.message(IsAdmin(), admin_states.JobStates.description, F.text.casefold() != 'отмена')
async def admin_add_project_description(message: Message, state: FSMContext) -> None:
    """Create Project description Command Reply"""
    await state.update_data(description=message.text)
    await state.set_state(admin_states.JobStates.technology)
    await message.answer(**admin_text.JOBS_TITLE_TECHNOLOGY.as_kwargs())


@router.message(IsAdmin(), admin_states.JobStates.technology, F.text.casefold() != 'отмена')
async def admin_add_project_technology(message: Message, state: FSMContext) -> None:
    """Create Project technology Command Reply"""
    await state.update_data(technology=message.text)
    await state.set_state(admin_states.JobStates.images)
    await message.answer(**admin_text.JOBS_TITLE_IMAGES.as_kwargs())


@router.message(IsAdmin(),
                F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]),
                admin_states.JobStates.images)
async def admin_add_project_images(message: Message,
                                   state: FSMContext,
                                   session: AsyncSession,
                                   album: list[Message] = None) -> None:
    """Create Project Save Command Reply"""
    data: dict = await state.get_data()
    await state.clear()
    # Create Project
    project_id: int = await service_admin.create_project(
        data['title'],
        data['description'],
        data['technology'],
        message,
        session,
    )
    if project_id:
        # Get Files Names
        files_name: list[str] = await utils_func.get_files_name_download_file(message, album)
        # Added To Database
        await service_admin.create_image_project(project_id, files_name, message, session)


@router.callback_query(IsAdmin(), F.data == 'change_project')
async def admin_change_project_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Change Project Command Inline"""
    count_jobs: int = await service_admin.get_count_projects(session=session)
    if count_jobs:
        await utils_func.delete_before_message(callback)
        await pagination(
            type_='projects',
            message=callback.message,
            callback_back='back_to_settings',
            callback_type='admin',
            session=session,
        )
    else:
        await callback.message.answer(admin_text.NOT_EXISTS_JOBS)


@router.callback_query(IsAdmin(), F.data.startswith('projects_admin_№'))
async def admin_get_project_info_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Get Project Information Command Inline"""
    await utils_func.output_info_project(callback, session, type_user='admin')


@router.callback_query(IsAdmin(), F.data.startswith('publish_project_') | F.data.startswith('unpublish_project_'))
async def admin_edit_show_project_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Edited Project Visibility Command Inline"""
    data: list[str] = callback.data.split('_')
    project_id: int = int(data[-1])
    deleted: bool = False if data[0] == 'publish' else True
    await service_admin.change_show_project(project_id, deleted, callback.message, session)


@router.callback_query(IsAdmin(), F.data.startswith('edit_project_'))
async def admin_edit_project_info_command_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """Edited Project Information Command Inline"""
    data: list[str] = callback.data.split('_')
    project_id: int = int(data[-1])
    field_edited: str = data[2]
    cancel_button = await user_reply_keyboard.cancel_reply_keyboard()

    await state.update_data(field=field_edited, project_id=project_id)

    if field_edited != 'images':
        await state.set_state(admin_states.ProjectEditStates.text)
        await state.update_data(images=None)
        await callback.message.answer(
            await admin_text.edited_project_text(field_edited),
            reply_markup=cancel_button,
        )
    else:
        await state.set_state(admin_states.ProjectEditStates.images)
        await state.update_data(text=None)
        await callback.message.answer(
            admin_text.EDITED_PROJECT_TEXT,
            reply_markup=cancel_button,
        )


@router.message(IsAdmin(), admin_states.ProjectEditStates.text, F.text.casefold() != 'отмена')
async def admin_save_info_project(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Save Edited Project Information Command Reply"""
    await state.update_data(text=message.text)
    data: dict = await state.get_data()
    await state.clear()
    values: dict = {data['field']: data['text']}
    # Change Project Information
    await service_admin.change_project_info(
        project_id=data.get('project_id'),
        values=values,
        message=message,
        session=session,
    )
    await admin_start_command(message)


@router.message(IsAdmin(),
                F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]),
                admin_states.ProjectEditStates.images)
async def admin_edit_project_images(message: Message,
                                    state: FSMContext,
                                    session: AsyncSession,
                                    album: list[Message] = None) -> None:
    data: dict = await state.get_data()
    project_id: int = data['project_id']
    await state.clear()
    # UnShow Images Projects
    un_show_images = await service_admin.un_show_images_project(project_id, message, session)
    if un_show_images:
        # Get Files Names
        files_name: list[str] = await utils_func.get_files_name_download_file(message, album)
        # Added To Database
        await service_admin.create_image_project(project_id, files_name, message, session)


# ================================================================= Settings Studio
@router.callback_query(IsAdmin(), F.data == 'settings_studio')
async def admin_settings_studio_command_inline(callback: CallbackQuery) -> None:
    """Settings Studio Menu Inline Command"""
    buttons = await admin_inline_keyboard.settings_studio_inline_keyboards()
    await callback.message.answer(
        admin_text.SETTINGS_STUDIO_MENU_TEXT,
        reply_markup=buttons,
    )


# ================================================================= Settings Studio - Tech Support

@router.callback_query(IsAdmin(), F.data == 'studio_tech_support')
async def admin_settings_tech_support_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Settings Tech Support Menu Inline Command"""
    # Check Exists Tech Support
    is_exist: bool = await service_admin.check_exist_tech_support(session)
    buttons = await admin_inline_keyboard.settings_tech_support_inline_keyboards(is_exist)
    await callback.message.answer(
        admin_text.SETTINGS_STUDIO_MENU_TEXT,
        reply_markup=buttons,
    )


@router.callback_query(IsAdmin(), F.data.in_({'add_tech_support', 'edit_tech_support'}))
async def admin_add_tech_support_command_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """Add Tech Support Command Inline"""
    cancel_button = await user_reply_keyboard.cancel_reply_keyboard()
    await state.set_state(admin_states.TechSupport.username)
    await callback.message.answer(
        **admin_text.ADD_TECH_SUPPORT_USERNAME.as_kwargs(),
        reply_markup=cancel_button,
    )


@router.message(IsAdmin(), admin_states.TechSupport.username, F.text.casefold() != 'отмена')
async def admin_add_tech_support_username(message: Message, state: FSMContext) -> None:
    """Add Tech Support Username Command reply"""
    if not message.text:
        await message.answer(**admin_text.ADD_TECH_SUPPORT_USERNAME.as_kwargs())
        return
    await state.update_data(username=message.text)
    await state.set_state(admin_states.TechSupport.email)
    await message.answer(**admin_text.ADD_TECH_SUPPORT_EMAIL.as_kwargs())


@router.message(IsAdmin(), admin_states.TechSupport.email, F.text.casefold() != 'отмена')
async def admin_add_tech_support_email(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Add Tech Support Email Command reply"""
    # Check Is Email
    is_email: bool = utils_func.check_is_email(message.text)
    if not is_email:
        await message.answer(admin_text.NOT_VALID_EMAIL_TEXT)
        return

    # Get State Data
    await state.update_data(email=message.text)
    data: dict = await state.get_data()
    await state.clear()

    # Check Exists Tech Support
    is_exist: bool = await service_admin.check_exist_tech_support(session)
    if is_exist:
        # Update To Database
        await service_admin.update_tech_support(**data, message=message, session=session)
    else:
        # Added To Database
        await service_admin.create_tech_support(**data, message=message, session=session)


@router.callback_query(IsAdmin(), F.data == 'show_tech_support')
async def admin_show_tech_support_command_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    """Show Tech Support Command Inline"""
    tech_support = await service_admin.get_tech_support(session)
    await callback.message.answer(
        admin_text.TECH_SUPPORT_INFO.format(
            username=tech_support.username,
            email=tech_support.email,
        ),
        parse_mode=ParseMode.HTML,
    )
