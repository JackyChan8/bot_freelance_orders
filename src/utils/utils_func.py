import os
import re
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram import Bot

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import decorate_logging
from src.services import services as service_user
from src.utils.text import user as user_text
from src.utils.text import admin as admin_text
from src.utils import static_path
from src.utils.keyboards.inline import user as user_inline_keyboard
from src.utils.keyboards.inline import admin as admin_inline_keyboard


statuses = {
    'new': 'Рассмотрение',
    'coord': 'Согласование',
    'work': 'В работе',
    'test': 'Тестирование',
    'finish': 'Завершенный',
}

EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


@decorate_logging
async def delete_before_message(callback: CallbackQuery) -> None:
    """Delete Before Message"""
    await callback.message.delete()


@decorate_logging
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


@decorate_logging
async def get_referral_users(user_id: int, callback: CallbackQuery, session: AsyncSession) -> str:
    """Get Referral Users"""
    users = await service_user.get_referral_users_id(user_id, session)
    chat_members = [await callback.bot.get_chat_member(user, user) for user in users]
    return '\n'.join([f'@{member.user.username}' for member in chat_members])


@decorate_logging
async def output_info_order(order_id: int, order, message: Message, session: AsyncSession, is_admin: bool = False):
    """Output Information Order"""
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
        if is_admin:
            buttons = await admin_inline_keyboard.get_order_info_inline_keyboard(order_id, is_task=True)
        else:
            buttons = await user_inline_keyboard.get_tech_task_inline_keyboard(order_id)
    else:
        if is_admin:
            buttons = await admin_inline_keyboard.get_order_info_inline_keyboard(order_id)
    await message.answer(text, reply_markup=buttons, parse_mode=ParseMode.HTML)


@decorate_logging
async def output_info_promo_code(
        promo_code_id: int,
        promo_code,
        message: Message,
        is_admin: bool = False):
    """Output Information Promo Code"""
    # Generate text
    text: str = await user_text.show_info_promo_code(promo_code_id, promo_code.discount, promo_code.created_at)

    if is_admin:
        buttons = await admin_inline_keyboard.get_promo_code_info_inline_keyboard(promo_code_id)
    else:
        buttons = await user_inline_keyboard.apply_promo_code_inline_keyboard(promo_code_id)
    await message.answer(text, reply_markup=buttons, parse_mode=ParseMode.HTML)


@decorate_logging
async def output_info_review(
        review_id: int,
        message: Message,
        session: AsyncSession,
        is_admin: bool = False) -> None:
    """Output Information Review"""
    # Get Review
    review = await service_user.get_review_by_id(review_id, session)
    # Get Author Review Username
    review_author = await message.bot.get_chat_member(review.author, review.author)
    # Generate Text
    text: str = await user_text.show_info_review(
        review.id,
        review_author.user.username,
        review.message,
        review.rating,
        review.created_at
    )
    # Generate Buttons
    buttons = None
    if is_admin:
        buttons = await admin_inline_keyboard.get_review_info_inline_keyboard(review.id, review.is_publish)
    await message.answer(text, reply_markup=buttons, parse_mode=ParseMode.HTML)


@decorate_logging
async def output_info_project(callback: CallbackQuery, session: AsyncSession, type_user: str = 'user'):
    """Output Information Project"""
    project_id: int = int(callback.data.split('№')[-1])
    # Get Project
    project = await service_user.get_project_by_id(project_id, session)
    # Output Information Project
    if type_user == 'user':
        buttons = await user_inline_keyboard.get_project_info_inline_keyboard(project_id)
    else:
        buttons = await admin_inline_keyboard.get_project_info_inline_keyboard(project_id, project.deleted)
    await callback.message.answer(
        admin_text.JOBS_INFO_TEXT.format(
            title=project.title,
            description=project.description,
            technology=project.technology,
            project_created=project.created_at,
        ),
        reply_markup=buttons,
    )


@decorate_logging
async def get_files_name_download_file(message: Message, album: list[Message] = None) -> list[str]:
    """Get Files Names About Files"""
    files_names: list[str] = []
    # Check Group or Simple File
    if album:
        files_id: list[str] = []
        # Get Files ID
        for msg in album:
            file_id: str = await get_files(msg)
            files_id.append(file_id)
        # Save Files
        for file_id in files_id:
            path_file: str = await save_document(file_id, message)
            files_names.append(path_file)
    else:
        file_id: str = await get_files(message)
        path_file: str = await save_document(file_id, message)
        files_names.append(path_file)
    return files_names


@decorate_logging
async def send_bot_message(bot: Bot, chat_id: int, text: str) -> None:
    """Send Message Bot"""
    await bot.send_message(chat_id, text)


@decorate_logging
async def save_document(file_id: int, message: Message) -> str:
    """Save Document"""
    file = await message.bot.get_file(file_id)
    _, file_extension = os.path.splitext(file.file_path)
    file_name: str = message.date.now().strftime('%m_%d_%Y_%H_%M_%S') + f'_{file_id}' + file_extension
    destination = static_path.JOBS_FILES + file_name
    await message.bot.download(file=file_id, destination=destination)
    return file_name


@decorate_logging
async def get_files(message: Message) -> str:
    """Get Files From Message"""
    if message.photo:
        file_id: str = message.photo[-1].file_id
    else:
        obj_dict = message.dict()
        file_id: str = obj_dict[message.content_type]['file_id']
    return file_id


@decorate_logging
def check_is_email(text: str) -> bool:
    """Check Regex is Email Address"""
    if re.fullmatch(EMAIL_REGEX, text):
        return True
    else:
        return False
