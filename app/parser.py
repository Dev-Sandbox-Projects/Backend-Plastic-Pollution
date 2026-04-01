import pandas as pd
import requests
import json
from io import StringIO
from config import settings
from app.database import r

def fetch_and_store():
    URL = settings.URL_TOTAL
    response = requests.get(URL, headers={"Accept": "text/csv"})
    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text))
        df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
        global_data = df.groupby('TIME_PERIOD')['OBS_VALUE'].sum().reset_index().to_dict(orient='records')
        r.set("plastic_data", json.dumps(global_data))
        print("Данные обновлены в Redis!")
