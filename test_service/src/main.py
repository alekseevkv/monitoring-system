from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.stable_api import router as stable_router
from src.api.v1.unstable_api import router as unstable_router
from src.api.v1.others_api import router as other_router

app = FastAPI(
    title="Test Service",
    description="Тестовый сервис для демонстрации работы системы мониторинга",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stable_router, prefix="", tags=["Cтабильные endpoint'ы"])
app.include_router(unstable_router, prefix="/api/v1/products", tags=["Нестабильные endpoint'ы"])
app.include_router(other_router, prefix="", tags=["Другие endpoint'ы"])