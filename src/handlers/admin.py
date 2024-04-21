from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from sqlalchemy.ext.asyncio import AsyncSession

from services import services as service_admin
from utils import utils_func
from utils.filters import IsAdmin
from utils.text import admin as admin_text
from utils.keyboards.inline import admin as admin_inline_keyboard
from utils.keyboards.reply import admin as admin_reply_keyboard
from utils.pagination import pagination

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


# ================================================================= Users
@router.message(IsAdmin(), F.text == '👤 Пользователи')
async def admin_users_command_reply(message: Message, session: AsyncSession):
    pass
