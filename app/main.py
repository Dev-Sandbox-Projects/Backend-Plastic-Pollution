from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.parser import update_global_plastic_data
from app.route import router
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.telegram import notify_all

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
    scheduler.add_job(update_global_plastic_data, CronTrigger(hour=0, minute=0), id="oecd_job")
    scheduler.start()
    async def run_initial_logic():
        try:
            logger.info("Run parser at server startup")
            loop = asyncio.get_running_loop()
            notify_all("Server running successful")
            await loop.run_in_executor(None, update_global_plastic_data)
            logger.info("Primary data has been successfully loaded into memory")
        except Exception as e:
            logger.error(f"Error at start: {e}")
            notify_all("Error starting server")
    asyncio.create_task(run_initial_logic())
    yield
    scheduler.shutdown()
    logger.info("Lifespan shutdown complete.")


app = FastAPI(lifespan=lifespan)

origins = [
    "https://dev-sandbox-projects.github.io",
    "https://vargkernel.github.io",

]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)