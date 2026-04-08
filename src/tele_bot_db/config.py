from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import os

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), ".env"))

    # Описываем поля и их типы
    TELEGRAM_BOT_TOKEN: SecretStr = SecretStr("secret")
    DATABASE_URL: SecretStr = SecretStr("secret")
    PORT: int = 8080
    LOG_LEVEL: str = "INFO"