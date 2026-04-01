from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    URL_TOTAL: str
    REDIS_URL: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        extra='ignore'
    )

settings = Settings()
