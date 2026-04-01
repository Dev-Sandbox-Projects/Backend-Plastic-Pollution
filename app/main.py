from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Добавлен импорт для CORS
from app.parser import fetch_and_store
from app.route import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Парсинг данных при запуске приложения
        fetch_and_store() # 
        print("Date successful parsed")
    except Exception as e:
        print(f"Failed: {e}")
    yield


app = FastAPI(lifespan=lifespan)

# Настройка CORS для разрешения запросов с вашего фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vargkernel.github.io", 
        "https://dev-sandbox-projects.github.io",
        "http://localhost:5173",                   # Для локальной разработки (Vite)
        "http://localhost:3000",                   # Для локальной разработки (другие порты)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

app.include_router(router) # Подключение маршрутов из route.py
