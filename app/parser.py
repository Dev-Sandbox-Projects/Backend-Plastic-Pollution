import json
from io import StringIO

import pandas as pd
import requests

from app.utils import send_telegram_msg
from config import settings
from app.database import r


def _read_oecd_csv(url: str) -> pd.DataFrame | None:
	print(f">>> [DEBUG] Запрос к OECD: {url[:60]}...", flush=True)
	try:
		r_req = requests.get(url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
		print(f">>> [DEBUG] Ответ получен. Status: {r_req.status_code}", flush=True)

		if r_req.status_code != 200:
			print(f"OECD ERROR: {url[:80]}… → HTTP {r_req.status_code}", flush=True)
			return None

		print(f">>> [DEBUG] Чтение CSV через Pandas...", flush=True)
		df = pd.read_csv(StringIO(r_req.text), sep=None, engine="python")
		df.columns = [c.upper() for c in df.columns]

		if "OBS_VALUE" not in df.columns or "TIME_PERIOD" not in df.columns:
			print(f"OECD ERROR: нет TIME_PERIOD/OBS_VALUE, колонки: {list(df.columns)}", flush=True)
			return None

		df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
		df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")

		result_df = df.dropna(subset=["TIME_PERIOD", "OBS_VALUE"])
		print(f">>> [DEBUG] CSV успешно обработан. Строк: {len(result_df)}", flush=True)
		return result_df

	except Exception as e:
		print(f">>> [DEBUG] Ошибка внутри _read_oecd_csv: {e}", flush=True)
		return None


def fetch_and_store():
	try:
		print(">>> [DEBUG] Старт fetch_and_store", flush=True)

		print("Запрос OECD (график)…", flush=True)
		df = _read_oecd_csv(settings.URL_TOTAL)

		if df is None:
			print(">>> [DEBUG] Аварийный выход: df is None", flush=True)
			return
		if df.empty:
			print(">>> [DEBUG] Аварийный выход: df is empty", flush=True)
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

		print(">>> [DEBUG] Попытка записи в Redis...", flush=True)
		r.set("plastic_data", json.dumps(global_data))
		r.set("plastic_cards", json.dumps(cards))
		message = f"OK Redis: график до {last_year} г., последнее значение {prod_val} Mt."
		print(message, flush=True)
		try:
			for chat in settings.CHAT_IDS:
				send_telegram_msg(settings.TOKEN, chat, message)
		except Exception as tg_err:
			print(f"⚠️ Не удалось отправить лог в Telegram: {tg_err}", flush=True)


	except Exception as e:
		print(f"Failed: {e}", flush=True)