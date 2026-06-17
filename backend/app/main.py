"""FastAPI application entrypoint.

Wires CORS for the Next.js frontend, creates tables on startup (so the app runs
with zero migration steps), and mounts the routers under ``/api/v1``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import dependants, e2e
from app.core.config import settings
from app.core.db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on boot — no migration step required to run locally.
    create_db_and_tables()
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(dependants.router, prefix=settings.API_V1_PREFIX)
app.include_router(e2e.router, prefix=settings.API_V1_PREFIX)
