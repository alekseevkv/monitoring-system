from fastapi import status, APIRouter, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils import count, now

router = APIRouter()
security = HTTPBearer(auto_error=False)

BASE = "http://test-service:8001"

@router.delete(
    "/api/v1/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар (всегда 500)"
)
async def delete_product(product_id: int = Path(..., ge=1, le=1000)):
    n = count("delete_product")
    raise HTTPException(
        status_code=500,
        detail={
            "error": "internal_server_error",
            "timestamp": now(),
            "request_number": n
        },
    )

@router.get(
    "/api/v1/admin",
    status_code=status.HTTP_200_OK,
    summary="Требует авторизации Bearer token (200 или 401)"
)
async def secure_admin(
    auth: HTTPAuthorizationCredentials | None = Depends(security)
):
    if auth is None or auth.credentials != "secret-123":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthorized",
                "message": "Требуется Bearer токен: {'Authorization': 'Bearer secret-123'}",
                "timestamp": now()
            },
        )
    return {
        "status": "ok",
        "user": "admin",
        "timestamp": now()
    }

@router.options(
    "/api/v1/products",
    status_code=status.HTTP_200_OK,
    summary="Ответ с кастомными заголовками (200)"
)
async def custom_headers():
    return JSONResponse(
        content={},
        headers={
            "Allow": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Origin": "",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",
        }
    )

@router.get(
    "/info",
    summary="Информация о тестовом сервисе"
)
async def info():
    return {
        "endpoints": [
            {
                "name": "Ping",
                "description": "HEAD /ping → 200 OK",
                "url": f"{BASE}/ping",
                "headers": {},
                "timeout": 5,
                "http_method": "HEAD",
                "expected_status_code": 200
            },
            {
                "name": "Создать товар",
                "description": "POST /api/v1/products → 201 Created",
                "url": f"{BASE}/api/v1/products",
                "headers": {},
                "timeout": 5,
                "http_method": "POST",
                "expected_status_code": 201
            },
            {
                "name": "Обновить товар",
                "description": "PUT /api/v1/products/1 → 200 OK",
                "url": f"{BASE}/api/v1/products/1",
                "headers": {},
                "timeout": 5,
                "http_method": "PUT",
                "expected_status_code": 200
            },
            {
                "name": "Каталог товаров",
                "description": "GET /api/v1/products → 50% - 200 OK, 50% - 500 Internal Server Error",
                "url": f"{BASE}/api/v1/products",
                "headers": {},
                "timeout": 5,
                "http_method": "GET",
                "expected_status_code": 200
            },
            {
                "name": "Частично обновить товар",
                "description": "PATCH /api/v1/products/1 → 200 OK, каждый 3-й запрос - 503 Service Unavailable",
                "url": f"{BASE}/api/v1/products/1",
                "headers": {},
                "timeout": 5,
                "http_method": "PATCH",
                "expected_status_code": 200
            },
            {
                "name": "Генерация отчёта (1-10 сек)",
                "description": "GET /api/v1/products/report → 200 OK или timeout",
                "url": f"{BASE}/api/v1/products/report",
                "headers": {},
                "timeout": 5,
                "http_method": "GET",
                "expected_status_code": 200
            },
            {
                "name": "Удалить товар (всегда 500)",
                "description": "DELETE /api/v1/products/1 → 500 Internal Server Error",
                "url": f"{BASE}/api/v1/products/1",
                "headers": {},
                "timeout": 5,
                "http_method": "DELETE",
                "expected_status_code": 200
            },
            {
                "name": "Требует авторизации",
                "description": "GET /api/v1/admin → 200 OK или 401 Unauthorized",
                "url": f"{BASE}/api/v1/admin",
                "headers": {
                "Authorization": "Bearer secret-123"
                },
                "timeout": 5,
                "http_method": "GET",
                "expected_status_code": 200
            },
            {
                "name": "Ответ с кастомными заголовками",
                "description": "OPTIONS /api/v1/products → 200 OK",
                "url": f"{BASE}/api/v1/products",
                "headers": {
                    "Origin": "http://backend:8000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                    },
                "timeout": 5,
                "http_method": "OPTIONS",
                "expected_status_code": 200
            }
        ],
        "timestamp": now()
    }