from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    url: str = Field(min_length=1, default="postgresql+asyncpg://root:root@localhost:5432/quest")

    model_config = SettingsConfigDict(env_prefix="v1_db_")
