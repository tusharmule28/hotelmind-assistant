from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.intent_router import router as intent_router
from app.api.pms_router import router as pms_router
from app.api.hitl_router import router as hitl_router
from app.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log service initialization settings
    logger.info(
        "service_starting",
        app_name=settings.APP_NAME,
        ollama_url=settings.OLLAMA_BASE_URL,
        ollama_model=settings.OLLAMA_MODEL,
        threshold=settings.CONFIDENCE_THRESHOLD
    )
    yield
    logger.info("service_shutting_down")

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready FastAPI service for AI hotel assistant intent classification.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration for production readiness
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(intent_router)
app.include_router(pms_router)
app.include_router(hitl_router)

@app.get("/health", tags=["health"])
async def health_check():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME
    }
