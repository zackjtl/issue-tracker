"""Main application."""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import init_db

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    os.makedirs(settings.ISSUES_DATA_DIR, exist_ok=True)
    os.makedirs(settings.ATTACHMENTS_DIR, exist_ok=True)
    await init_db()

    # Log the effective CORS origins so misconfiguration is immediately visible
    # in the deployment logs.
    allowed_origins = settings.get_cors_origins()
    logger.info("CORS allowed origins (%d): %s", len(allowed_origins), allowed_origins)

    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Build the allowed-origins list once at startup via the helper that also
# folds in FRONTEND_URL.
_cors_origins = settings.get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api import auth_supabase, projects, issues

app.include_router(auth_supabase.router)
app.include_router(projects.router)
app.include_router(issues.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


@app.get("/debug/cors")
async def debug_cors():
    """Return the active CORS configuration.

    Useful for verifying that the CORS_ORIGINS / FRONTEND_URL environment
    variables have been picked up correctly without having to dig through
    deployment logs.
    """
    return {
        "cors_origins_raw": settings.CORS_ORIGINS,  # comma-separated string
        "frontend_url": settings.FRONTEND_URL,
        "effective_origins": settings.get_cors_origins(),
    }
