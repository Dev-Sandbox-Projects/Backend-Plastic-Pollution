from io import StringIO
import pandas as pd
import requests
from app.telegram import notify_all
from config import settings

GLOBAL_PLASTIC_GRAPH = []  # Данные для графика
GLOBAL_PLASTIC_CARDS = {}  # Данные для карточек


def _read_oecd_csv(url: str) -> pd.DataFrame | None:
	try:
		r_req = requests.get(url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
		if r_req.status_code != 200:
			return None
		df = pd.read_csv(StringIO(r_req.text), sep=None, engine="python")
		df.columns = [c.upper() for c in df.columns]
		if "OBS_VALUE" not in df.columns or "TIME_PERIOD" not in df.columns:
			return None
		df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
		df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")
		return df.dropna(subset=["TIME_PERIOD", "OBS_VALUE"])
	except Exception:
		return None


def update_global_plastic_data():
	global GLOBAL_PLASTIC_GRAPH, GLOBAL_PLASTIC_CARDS
	try:
		print("Launch of OECD data update...", flush=True)
		df = _read_oecd_csv(settings.URL_TOTAL)
		if df is None or df.empty:
			print("[ERROR] OECD Total data is empty/None")
			return
		res = (
			df.groupby("TIME_PERIOD", as_index=False)["OBS_VALUE"]
			.max()
			.sort_values("TIME_PERIOD")
		)
		res["OBS_VALUE"] = res["OBS_VALUE"].round(0).astype(int)
		GLOBAL_PLASTIC_GRAPH = res.to_dict(orient="records")

		last = res.iloc[-1]
		last_year = int(last["TIME_PERIOD"])
		prod_val = int(last["OBS_VALUE"])

		GLOBAL_PLASTIC_CARDS = {
			"year_production": last_year,
			"tons_produced_annually_mton": prod_val,
			"year_ocean_leakage": 2019,
			"tons_enter_oceans_mton": 22,
			"marine_animals_affected_millions": 100,
			"ocean_plastic_particles_trillions": 171,
		}
		notify_all(f"OECD Update: {GLOBAL_PLASTIC_CARDS['year_production']} yr, {GLOBAL_PLASTIC_CARDS['tons_produced_annually_mton']} Mt.")

	except Exception as e:
		notify_all(f"[ERROR] Update failed: {e}")

def get_plastic_stats():
	return {
		"graph": GLOBAL_PLASTIC_GRAPH,
		"cards": GLOBAL_PLASTIC_CARDS
	}
