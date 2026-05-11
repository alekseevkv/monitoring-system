from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.monitoring_task_api import router as monitoring_tasks_router
from src.configs.app import settings

app = FastAPI(
    title=settings.app.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
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
    prefix="/api/v1/monitoring_tasks",
    tags=["Задачи мониторинга"],
)
