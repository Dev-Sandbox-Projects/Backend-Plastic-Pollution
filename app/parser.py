import json
from io import StringIO

import pandas as pd
import requests

from config import settings
from app.database import r


def _read_oecd_csv(url: str) -> pd.DataFrame | None:
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        print(f"OECD: {url[:80]}… → HTTP {r.status_code}")
        return None
    df = pd.read_csv(StringIO(r.text), sep=None, engine="python")
    df.columns = [c.upper() for c in df.columns]
    if "OBS_VALUE" not in df.columns or "TIME_PERIOD" not in df.columns:
        print(f"OECD: нет TIME_PERIOD/OBS_VALUE, колонки: {list(df.columns)}")
        return None
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")
    return df.dropna(subset=["TIME_PERIOD", "OBS_VALUE"])


def fetch_and_store():
    """
    Кладёт в Redis:
    - plastic_data: [{TIME_PERIOD, OBS_VALUE}, …] — одно значение на год (млн тонн, целые).
    - plastic_cards: метрики по последнему доступному году (карточки).
    """
    try:
        print("Запрос OECD (график)…")
        df = _read_oecd_csv(settings.URL_TOTAL)
        if df is None or df.empty:
            return
        res = (
            df.groupby("TIME_PERIOD", as_index=False)["OBS_VALUE"]
            .max()
            .sort_values("TIME_PERIOD")
        )
        res["OBS_VALUE"] = res["OBS_VALUE"].round(0).astype(int)
        global_data = res.to_dict(orient="records")

        last = res.iloc[-1]
        last_year = int(last["TIME_PERIOD"])
        prod_val = int(last["OBS_VALUE"])

        ocean_mton: int | None = None
        ocean_year: int | None = None
        if settings.URL_CARD_OCEAN:
            print("Запрос OECD (карточка: океан)…")
            odf = _read_oecd_csv(settings.URL_CARD_OCEAN)
            if odf is not None and not odf.empty:
                oagg = odf.groupby("TIME_PERIOD", as_index=False)["OBS_VALUE"].max()
                oagg = oagg.sort_values("TIME_PERIOD")
                last_o = oagg.iloc[-1]
                ocean_year = int(last_o["TIME_PERIOD"])
                ocean_mton = int(round(float(last_o["OBS_VALUE"]), 0))

        cards = {
            "year_production": last_year or 2019,
            "tons_produced_annually_mton": prod_val or 460,
            "year_ocean_leakage": ocean_year or 2019,
            "tons_enter_oceans_mton": ocean_mton or 22,
            "marine_animals_affected_millions": 100,
            "ocean_plastic_particles_trillions": 171,
        }

        r.set("plastic_data", json.dumps(global_data))
        r.set("plastic_cards", json.dumps(cards))

        print(f"OK Redis: график до {last_year} г., последнее значение {prod_val} Mt.")

    except Exception as e:
        print(f"Failed: {e}")
