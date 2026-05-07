# Neighborhood Library — backend + proto + frontend
# Build: docker compose build
# Run:  docker compose up --build

FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "grpcio-tools>=1.62"

COPY pyproject.toml README.md ./
COPY proto ./proto
COPY scripts ./scripts
COPY backend ./backend

RUN chmod +x scripts/compile_protos.sh scripts/docker-entrypoint-backend.sh \
    && ./scripts/compile_protos.sh \
    && pip install --no-cache-dir ".[dev]"

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 50051 8000

ENTRYPOINT ["/app/scripts/docker-entrypoint-backend.sh"]
