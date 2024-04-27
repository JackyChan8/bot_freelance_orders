from aiogram.types import Message
from aiogram.filters import BaseFilter

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.services import services


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.ADMINS_ID


class IsBanUser(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        user_id: int = message.from_user.id
        is_blocked: int = await services.check_is_blocked_users(user_id, session)
        if is_blocked:
            return False
        else:
            return True

