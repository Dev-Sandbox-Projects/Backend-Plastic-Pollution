import os
import json
import redis
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from io import StringIO
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import settings

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(redis_url, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        fetch_and_store()
        print("Data successful parsed")
    except Exception as e:
        print(f"Failed: {e}")
    yield

def fetch_and_store():
    URL = settings.URL_TOTAL
    response = requests.get(URL, headers={"Accept": "application/xml"})
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        data_list = []

        for obs in root.findall(".//{*}Obs"):
            row = {}
            for val in obs.findall(".//{*}Value"):
                row[val.get("id")] = val.get("value")

            obs_val = obs.find(".//{*}ObsValue")
            if obs_val is not None:
                row["OBS_VALUE"] = obs_val.get("value")
            
            data_list.append(row)

        df = pd.DataFrame(data_list)
        
        df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
        global_data = df.groupby('TIME_PERIOD')['OBS_VALUE'].sum().reset_index().to_dict(orient='records')
        
        r.set("plastic_data", json.dumps(global_data))
        print("Данные обновлены в Redis (распарсен XML)!")

app = FastAPI(lifespan=lifespan)

@app.get("/plastic")
def get_plastic():
    data = r.get("plastic_data")
    if data:
        return json.loads(data)
    return {"error": "данные еще не загружены"}
