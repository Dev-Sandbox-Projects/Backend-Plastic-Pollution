from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.parser import fetch_and_store
from app.route import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        fetch_and_store()
        print("Date successful parsed")
    except Exception as e:
        print(f"Failed: {e}")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)