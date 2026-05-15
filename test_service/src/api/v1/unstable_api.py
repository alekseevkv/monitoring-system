import asyncio
import random

from fastapi import status, APIRouter, HTTPException, Path, Request

from src.utils import count, now, Product

router = APIRouter()

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Каталог товаров (50% - 200, 50% - 500)"
)
async def get_products():
    n = count("get_products")
    if random.random() < 0.5:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "timestamp": now(),
                "request_number": n
            },
        )
    return {
        "items": [
            {"id": 1, "name": "Ноутбук", "price": 89999, "in_stock": True},
            {"id": 2, "name": "Клавиатура", "price": 5999, "in_stock": True}
        ],
        "total": 2,
        "timestamp": now()
    }

@router.patch(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Частично обновить товар (200, каждый 3-й запрос - 503)"
)
async def patch_product(request: Request, body: Product, product_id: int = Path(..., ge=1, le=1000)):
    n = count("patch_product")
    if n % 3 == 0:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "timestamp": now(),
                "request_number": n
            },
        )
    return {
        "product_id": product_id,
        "payload": body.model_dump() if request.headers.get("content-type") == "application/json" else {},
        "updated_at": now(),
    }

@router.get(
    "/report",
    summary="Генерация отчёта 1-10 сек (200 или timeout)",
    status_code=status.HTTP_200_OK
)
async def get_report():
    delay = random.uniform(1.0, 10.0)
    await asyncio.sleep(delay)
    return {
        "status": "ok",
        "report_id": random.randint(1, 100),
        "generation_time_s": int(delay),
        "timestamp": now(),
    }