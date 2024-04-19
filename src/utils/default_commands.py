from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from utils.text import commands as text_commands


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description=text_commands.START_COMMAND),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
