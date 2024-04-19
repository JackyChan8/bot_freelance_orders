from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from utils import static_path as photo_user
from services import services as service_user


type_service = {
    'order': (service_user.get_filename_task_tech, ),
}

router = Router(name='file')


@router.callback_query(F.data.startswith('download_file_'))
async def download_file(callback: CallbackQuery, session: AsyncSession) -> None:
    """Download File"""
    user_id: int = callback.from_user.id
    data: list = callback.data.split('_')
    elem_id: int = int(data[-1])
    elem_type: str = data[-2]
    file_name: str = await type_service.get(elem_type)[0](elem_id, session)

    # Send Document To User
    file_path: str = photo_user.ORDERS_FILES + file_name
    file: FSInputFile = FSInputFile(file_path)
    await callback.bot.send_document(document=file, chat_id=user_id)
