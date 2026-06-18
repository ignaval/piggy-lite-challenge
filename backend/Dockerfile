# Backend image for local Docker development (hot-reload via bind mount).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install the project (runtime + dev tools + Postgres driver). Editable so the
# bind-mounted source in docker-compose hot-reloads. README.md is referenced by
# pyproject metadata, so it must be present at install time.
COPY pyproject.toml requirements.txt README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
RUN pip install -e ".[dev,postgres]"

EXPOSE 8000

# docker-compose overrides this to run migrations first; this is the fallback.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
