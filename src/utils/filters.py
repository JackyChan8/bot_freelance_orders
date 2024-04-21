from aiogram.types import Message
from aiogram.filters import BaseFilter

from config import settings


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.ADMINS_ID
