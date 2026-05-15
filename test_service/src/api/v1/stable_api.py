import random

from fastapi import Request, status, APIRouter, Path

from src.utils import now, Product

router = APIRouter()

@router.head(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Ping (200)",
)
async def ping():
    return {}

@router.post(
    "/api/v1/products",
    status_code=status.HTTP_201_CREATED,
    summary="Создать товар (201)"
)
async def create_product(request: Request, body: Product):
    return {
        "product_id": random.randint(1, 100),
        "payload": body.model_dump() if request.headers.get("content-type") == "application/json" else {},
        "created_at": now(),
    }

@router.put(
    "/api/v1/products/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Обновить товар (200)"
)
async def update_product(request: Request, body: Product, product_id: int = Path(..., ge=1, le=1000)):
    return {
        "product_id": product_id,
        "payload": body.model_dump() if request.headers.get("content-type") == "application/json" else {},
        "updated_at": now(),
    }