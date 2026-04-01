from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.parser import fetch_and_store
from app.route import router
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import r

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
    try:
        r.flushdb()
        logger.info(f"Redis database {G}successfully flushed{END}")
    except Exception as e:
        logging.error(f"Redis flush failed: {e}")
    scheduler = BackgroundScheduler()
    trigger_daily = CronTrigger(hour=0, minute=0)
    scheduler.add_job(
        fetch_and_store,
        trigger=trigger_daily,
        id="oecd_parser_job",
        replace_existing=True
    )
    scheduler.start()

    logger.info(f"Scheduler {G}launched{END}: OECD parsing once a day.")
    try:
        fetch_and_store()
        logger.info(f"Initial data {G}successfully parsed{END}")
    except Exception as e:
        logging.error(f"Initial fetch failed: {e}")

    yield
    scheduler.shutdown()
    logger.info(f"Scheduler {Y}stopped{END}.")


app = FastAPI(lifespan=lifespan)
app.include_router(router)