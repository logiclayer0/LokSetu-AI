import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import (
    connect_mongodb,
    close_mongodb,
    connect_redis,
    close_redis,
    connect_neo4j,
    close_neo4j,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongodb()
    await connect_redis()
    connect_neo4j()
    yield
    await close_mongodb()
    await close_redis()
    close_neo4j()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A Multilingual Digital Public Good for Citizen-Centric Infrastructure Planning",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.APP_ENV
        }
    )


from app.api.v1.api import api_router

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
