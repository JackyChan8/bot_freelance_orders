import asyncio

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from utils.default_commands import set_commands
from handlers import user, admin, echo, cancel, file, pagination
from middlewares import middlewares
from config import settings


async def main():
    engine = create_async_engine(settings.get_postgres_url(), echo=True)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    dp.update.middleware(middlewares.DbSessionMiddleware(session_pool=async_session_maker))

    await set_commands(bot)

    # Connect Routers
    dp.include_router(cancel.router)
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(file.router)
    dp.include_router(pagination.router)
    dp.include_router(echo.router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    print('Bot is Started')
    asyncio.run(main(), debug=False)
