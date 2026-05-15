from datetime import datetime, timezone
from pydantic import BaseModel

_request_counter: dict[str, int] = {}

def count(key: str) -> int:
    _request_counter[key] = _request_counter.get(key, 0) + 1
    return _request_counter[key]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

class Product(BaseModel):
    class Config:
        extra = "allow"