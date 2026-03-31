from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
	URL_TOTAL: str

	model_config = SettingsConfigDict(
		env_file=os.path.join(os.path.dirname(__file__), ".env")
	)


settings = Settings()
