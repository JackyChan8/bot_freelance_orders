import sys
import asyncio
from loguru import logger
from functools import wraps
from typing import Type, Any

from pydantic import SecretStr
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict

from src.utils.static_path import LOGS_PATH


class AdminsParse(EnvSettingsSource):
    def prepare_field_value(
            self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == 'ADMINS_ID':
            return [int(x) for x in value.split(',')]
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', case_sensitive=True)
    # Bot
    BOT_TOKEN: SecretStr
    ADMINS_ID: list[int]
    BOT_USERNAME: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASS: SecretStr
    POSTGRES_NAME: str

    # Testing
    POSTGRES_HOST_TEST: str
    POSTGRES_PORT_TEST: int
    POSTGRES_USER_TEST: str
    POSTGRES_PASS_TEST: SecretStr
    POSTGRES_NAME_TEST: str

    @staticmethod
    def build_postgres_url(user_db: str, pass_db: str, host_db: str,
                           port_db: int, db_name: str, protocol_db: str = 'postgresql+asyncpg') -> str:
        return f"{protocol_db}://{user_db}:{pass_db}@{host_db}:{port_db}/{db_name}"

    def get_postgres_url(self, is_prod: bool = True) -> str:
        """Get URL Postgres Database"""
        if is_prod:
            return self.build_postgres_url(user_db=self.POSTGRES_USER,
                                           pass_db=self.POSTGRES_PASS.get_secret_value(),
                                           host_db=self.POSTGRES_HOST,
                                           port_db=self.POSTGRES_PORT,
                                           db_name=self.POSTGRES_NAME)
        else:
            return self.build_postgres_url(user_db=self.POSTGRES_USER_TEST,
                                           pass_db=self.POSTGRES_PASS_TEST.get_secret_value(),
                                           host_db=self.POSTGRES_HOST_TEST,
                                           port_db=self.POSTGRES_PORT_TEST,
                                           db_name=self.POSTGRES_NAME_TEST)

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (AdminsParse(settings_cls),)

    # class Config:
    #     env_file = '.env'
    #     env_file_encoding = 'utf-8'


settings = BotSettings()

# Logging
logger.add(
    sys.stderr,
    colorize=True,
    format='<blue>{time}</blue> <green>{level}</green> <red>{message}</red>',
    filter='my_module',
    level='INFO',
)
logger.add(f'{LOGS_PATH}/file_1.log', rotation='100 MB', compression='zip')


def decorate_logging(fn):
    """Decorator for logging"""
    if asyncio.iscoroutinefunction(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:
                logger.patch(lambda r: r.update(function=fn.__name__)).error(f'({fn.__doc__}) - {exc}')
        return wrapper
    else:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                logger.patch(lambda r: r.update(function=fn.__name__, message=exc)).error(f'({fn.__doc__}) - {exc}')
        return wrapper
