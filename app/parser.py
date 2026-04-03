import pandas as pd
import requests
import time
from io import StringIO

from config import settings
from app.database import db

# Цвета для логов
G = "\033[92m"  # Зеленый
B = "\033[94m"  # Синий
R = "\033[91m"  # Красный
Y = "\033[93m"  # Желтый
END = "\033[0m" # Сброс

def _read_oecd_csv(url: str) -> pd.DataFrame | None:
    # Выводим полную ссылку без сокращений
    print(f">>> [DEBUG] Запрос к OECD: {url}", flush=True) 
    try:
        # ДОБАВЛЕН ИСКЛЮЧИТЕЛЬНО ACCEPT И USER-AGENT
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/csv'
        }
        
        r_req = requests.get(url, timeout=60, headers=headers)
        print(f">>> [DEBUG] Ответ получен. Status: {r_req.status_code}", flush=True)

        if r_req.status_code != 200:
            print(f"{R}OECD ERROR: HTTP {r_req.status_code} для URL: {url}{END}", flush=True)
            return None

        # Проверка на XML, чтобы не гадать по логам
        if r_req.text.strip().startswith("<?xml") or "<mes:Structure" in r_req.text:
            print(f"{R}>>> [CRITICAL] OECD проигнорировал Accept и прислал XML!{END}", flush=True)
            return None

        print(f">>> [DEBUG] Чтение CSV через Pandas...", flush=True)
        
        # ЗАМЕР ВРЕМЕНИ
        start_time = time.time()
        
        # Оптимизируем чтение: sep="," быстрее, чем None
        df = pd.read_csv(StringIO(r_req.text), sep=",")
        
        end_time = time.time()
        print(f"{Y}>>> [TIMER] Pandas обработал файл за {end_time - start_time:.2f} сек.{END}", flush=True)

        df.columns = [c.upper() for c in df.columns]

        if "OBS_VALUE" not in df.columns or "TIME_PERIOD" not in df.columns:
            print(f"{R}OECD ERROR: нет TIME_PERIOD/OBS_VALUE, колонки: {list(df.columns)}{END}", flush=True)
            return None

        df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
        df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")

        result_df = df.dropna(subset=["TIME_PERIOD", "OBS_VALUE"])
        print(f">>> [DEBUG] CSV успешно обработан. Строк: {len(result_df)}", flush=True)
        return result_df

    except Exception as e:
        print(f"{R}>>> [DEBUG] Ошибка внутри _read_oecd_csv: {e}{END}", flush=True)
        return None

def fetch_and_store():
    # ... (остальная часть функции остается без изменений)
    try:
        print(f"\n{G}>>> [DEBUG] Старт fetch_and_store{END}", flush=True)

        print("Запрос OECD (график)…", flush=True)
        df = _read_oecd_csv(settings.URL_TOTAL)

        if df is None or df.empty:
            print(f"{R}>>> [DEBUG] Аварийный выход: данные не получены{END}", flush=True)
            return

        print(">>> [DEBUG] Группировка данных графика...", flush=True)
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
            print("Запрос OECD (карточка: океан)…", flush=True)
            odf = _read_oecd_csv(settings.URL_CARD_OCEAN)
            if odf is not None and not odf.empty:
                print(">>> [DEBUG] Обработка данных океана...", flush=True)
                oagg = odf.groupby("TIME_PERIOD", as_index=False)["OBS_VALUE"].max()
                oagg = oagg.sort_values("TIME_PERIOD")
                last_o = oagg.iloc[-1]
                ocean_year = int(last_o["TIME_PERIOD"])
                ocean_mton = int(round(float(last_o["OBS_VALUE"]), 0))

        cards = {
            "year_production": last_year or 2019,
            "tons_produced_annually_mton": prod_val or 530,
            "year_ocean_leakage": ocean_year or 2019,
            "tons_enter_oceans_mton": ocean_mton or 22,
            "marine_animals_affected_millions": 100,
            "ocean_plastic_particles_trillions": 171,
        }

        db.set("plastic_data", global_data)
        db.set("plastic_cards", cards)

        print(f"\n{B}=== SNAPSHOT OF LOCAL DB ==={END}")
        print(f"CARDS: {cards}")
        print(f"GRAPH POINTS COUNT: {len(global_data)}")
        if len(global_data) > 6:
            print(f"DATA SAMPLE: {global_data[:3]} ... {global_data[-3:]}")
        else:
            print(f"DATA: {global_data}")
        print(f"{B}============================={END}\n")

        print(f"{G}OK Memory: данные обновлены. График до {last_year} г.{END}", flush=True)

    except Exception as e:
        print(f"{R}Failed in fetch_and_store: {e}{END}", flush=True)
