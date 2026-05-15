import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.check_result_api import router as check_result_router
from src.api.v1.monitoring_task_api import router as monitoring_tasks_router
from src.configs.app import settings
from src.helpers.monitoring_scheduler import monitoring_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    monitoring_scheduler.start()
    await monitoring_scheduler.load_from_db()
    yield
    monitoring_scheduler.shutdown()


app = FastAPI(
    title=settings.app.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(
    monitoring_tasks_router,
    prefix="/api/v1/monitoring-tasks",
    tags=["Задачи мониторинга"],
)
app.include_router(
    check_result_router,
    prefix="/api/v1",
    tags=["Результаты проверок и инциденты"],
)
