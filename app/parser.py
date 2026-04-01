from contextlib import asynccontextmanager

import redis
import pandas as pd
import requests
from fastapi import FastAPI
import json
from io import StringIO
from config import settings
import os

redis_url = os.getenv("REDIS_URL")
r = redis.from_url(redis_url, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        fetch_and_store()
        print("Date successful parsed")
    except Exception as e:
        print(f"Failed: {e}")
    yield

def fetch_and_store():
    URL = settings.URL_TOTAL
    response = requests.get(URL, headers={"Accept": "text/csv"})
    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text))
        df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
        global_data = df.groupby('TIME_PERIOD')['OBS_VALUE'].sum().reset_index().to_dict(orient='records')
        r.set("plastic_data", json.dumps(global_data))
        print("Данные обновлены в Redis!")


app = FastAPI(lifespan=lifespan)


@app.get("/plastic")
def get_plastic():
    data = r.get("plastic_data")
    if data:
        return json.loads(data)
    return {"error": "данные еще не загружены"}
