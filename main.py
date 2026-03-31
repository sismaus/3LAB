import schedule
import time
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.sync import sync_daily_data
from app.config import settings
from app.api.reports import router as reports_router
from app.api.sync_api import router as sync_router
from app.logging_config import logger

scheduler_thread = None
stop_scheduler = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler_thread, stop_scheduler
    stop_scheduler = False

    logger.info(f"Scheduling daily synchronization every {settings.sync_interval_minutes} minutes")
    schedule.every(settings.sync_interval_minutes).minutes.do(sync_daily_data)

    def run_scheduled_jobs():
        while not stop_scheduler:
            schedule.run_pending()
            time.sleep(1)

    scheduler_thread = threading.Thread(target=run_scheduled_jobs, daemon=True)
    scheduler_thread.start()

    yield

    logger.info("Shutting down the application")
    stop_scheduler = True
    if scheduler_thread and scheduler_thread.is_alive():
        scheduler_thread.join(timeout=5)

app = FastAPI(lifespan=lifespan)

app.include_router(reports_router, prefix="/api")
app.include_router(sync_router, prefix="/api")