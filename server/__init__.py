from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .core.databases.database_mongo import connect_mongo

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global database, client
    database, client = await connect_mongo()
    from .routes.user import check_auth, login, logout, reg
    from .routes import server_status
    try:
        yield
    finally:
        client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)