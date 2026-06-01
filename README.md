# Monitoring System

Система автоматического мониторинга доступности HTTP-эндпоинтов с отслеживанием инцидентов, расчётом SLA-метрик и уведомлением ответственных лиц о сбоях.

## Требования

- Docker и Docker Compose
- Python 3.14+ и uv
- Node.js 24+ и pnpm

---

## Запуск через Docker Compose

### Шаг 1 — Запустить базу данных

```bash
docker compose up db -d
```

Дождаться успешного прохождения healthcheck (обычно 10–15 секунд):

```bash
docker compose ps db
```

Статус должен быть `healthy`.

### Шаг 2 — Применить миграции

```bash
docker compose run --rm backend alembic upgrade head
```

### Шаг 3 — Запустить остальные сервисы

```bash
docker compose up --build backend web test-service
```

Для запуска в фоновом режиме:

```bash
docker compose up --build -d backend web test-service
```

После запуска сервисы доступны по адресам:

- Frontend — http://localhost:5173
- Backend API — http://localhost:8000
- API документация — http://localhost:8000/docs
- Тестовый сервис — http://localhost:8001

---

### Остановить все сервисы

```bash
docker compose down
```

### Остановить и удалить данные базы данных

```bash
docker compose down -v
```

---

## Запуск тестов

```bash
cd backend
uv run pytest
```
