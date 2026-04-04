from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    URL_TOTAL: str = Field(
        default=(
            "https://sdmx.oecd.org/public/rest/data/"
            "OECD.ENV.EEI,DSD_PU@DF_PU,1.0/"
            "W.PU_APP._Z.TOTAL.A._Z"
            "?dimensionAtObservation=AllDimensions&format=csv"
        ),
        description="Ряд для графика: TIME_PERIOD + OBS_VALUE (млн тонн).",
    )
    CHAT_IDS: list[int]
    TOKEN: str
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env")
    )


settings = Settings()
