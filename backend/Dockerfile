FROM ghcr.io/astral-sh/uv:python3.14-bookworm AS builder

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen --no-install-project

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY settings.toml .
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"
