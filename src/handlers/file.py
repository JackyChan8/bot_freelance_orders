from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, InputFile
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from utils.filters import IsBanUser, IsAdmin
from utils import static_path as photo_user
from services import services


type_service = {
    'order': (services.get_filename_task_tech, ),
}

router = Router(name='file')


@router.callback_query(IsBanUser(), F.data.startswith('download_file_'))
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


@router.callback_query(IsBanUser(), F.data.startswith('download_photos_project_'))
async def download_photos(callback: CallbackQuery, session: AsyncSession) -> None:
    """Download Photos Project"""
    project_id: int = int(callback.data.split('_')[-1])
    path_files: str = photo_user.JOBS_FILES

    # Get Images
    media_group = MediaGroupBuilder(caption=f'Фотографии Проекта: {project_id}')
    images = await services.get_images_project_by_id(project_id, session)
    for image in images:
        file: FSInputFile = FSInputFile(f'{path_files}{image}')
        media_group.add_photo(media=file)

    await callback.bot.send_media_group(chat_id=callback.from_user.id, media=media_group.build())
