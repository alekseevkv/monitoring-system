from fastapi import FastAPI

from src.api.v1.monitoring_task_api import router as monitoring_tasks_router
from src.configs.app import settings

app = FastAPI(
    title=settings.app.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(
    monitoring_tasks_router, prefix="/monitoring_tasks", tags=["Задачи мониторинга"]
)
