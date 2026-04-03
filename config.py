from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    # OECD SDMX 3: Global Plastics Outlook — «Plastics Use by Application», World, total (Mt).
    URL_TOTAL: str = Field(
        default=(
            "https://sdmx.oecd.org/public/rest/data/"
            "OECD.ENV.EEI,DSD_PU@DF_PU,1.0/"
            "W.PU_APP._Z.TOTAL.A._Z"
            "?dimensionAtObservation=AllDimensions&format=csv"
        ),
        description="Ряд для графика: TIME_PERIOD + OBS_VALUE (млн тонн).",
    )
    # Опционально: отдельный CSV-ряд для утечки в океан (тот же формат с TIME_PERIOD, OBS_VALUE).
    URL_CARD_OCEAN: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env")
    )


settings = Settings()
