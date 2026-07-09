from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.config import api_router
from app.core.config import settings
from app.db.engine import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Config Service", lifespan=lifespan)

if settings.SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(dsn=settings.SENTRY_DSN)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Config Service"}


@app.get("/health")
async def health():
    return {"status": "ok"}
