from fastapi import FastAPI
from src.configs.app import settings

app = FastAPI(
    title=settings.app.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
