from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.parser import fetch_and_store
from app.route import router
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import r
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import asyncio



G = "\033[92m"  # зеленый
B = "\033[94m"  # Синий
R = "\033[91m"  # Красный
Y = "\033[93m"  # Желтый
END = "\033[0m"  # Сброс цвета

logging.basicConfig(
	level=logging.INFO,
	format=f"{G}%(levelname)s{END}:     %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store, CronTrigger(hour=0, minute=0), id="oecd_job")
    scheduler.start()

    async def run_initial_logic():
        try:
            logger.info("Starting heavy initial fetch in background...")
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, fetch_and_store)
            logger.info("Background fetch task scheduled.")
        except Exception as e:
            logger.error(f"Failed to schedule initial fetch: {e}")
    background_task = asyncio.create_task(run_initial_logic())
    yield
    scheduler.shutdown()
    logger.info("Lifespan shutdown complete.")


app = FastAPI(lifespan=lifespan)

origins = [
    "https://dev-sandbox-projects.github.io/Plastic-Pollution-Report-2026/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)