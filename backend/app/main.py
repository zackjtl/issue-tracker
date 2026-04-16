"""Main application."""
import logging
import os
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.config import settings
from app.db.database import init_db, get_db

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CORSDebugMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every request's Origin header and the resulting
    Access-Control-Allow-Origin response header.

    Placed *before* CORSMiddleware in the stack (i.e. added to the app after
    CORSMiddleware) so it wraps the full request/response cycle and can
    inspect both the inbound Origin and the outbound CORS header that
    CORSMiddleware ultimately sets.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "<no Origin header>")
        logger.info(
            "[CORS-DEBUG] %s %s  |  Origin: %s",
            request.method,
            request.url.path,
            origin,
        )

        response: Response = await call_next(request)

        acao = response.headers.get(
            "access-control-allow-origin", "<header not set>"
        )
        logger.info(
            "[CORS-DEBUG] %s %s  |  Origin: %s  →  Access-Control-Allow-Origin: %s",
            request.method,
            request.url.path,
            origin,
            acao,
        )
        return response


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

# CORSDebugMiddleware is added AFTER CORSMiddleware so that Starlette places
# it outermost in the middleware stack.  It therefore sees the request before
# CORSMiddleware and the response after CORSMiddleware has set (or not set)
# the Access-Control-Allow-Origin header — giving us a full before/after log.
app.add_middleware(CORSDebugMiddleware)

# Include routers
from app.api import auth_supabase, projects, issues

app.include_router(auth_supabase.router)
app.include_router(projects.router)
app.include_router(issues.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler that logs the full traceback for every unhandled
    exception so that 500 errors are always visible in deployment logs."""
    tb = traceback.format_exc()
    logger.error(
        "[UNHANDLED EXCEPTION] %s %s\n"
        "Exception type : %s\n"
        "Exception value: %s\n"
        "Traceback:\n%s",
        request.method,
        request.url,
        type(exc).__name__,
        exc,
        tb,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
            "error": str(exc),
        },
    )


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
    """Health check with database connectivity test."""
    from sqlalchemy import text

    db_status = "unknown"
    db_error: str | None = None

    try:
        async for session in get_db():
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as exc:
        db_status = "error"
        db_error = f"{type(exc).__name__}: {exc}"
        logger.error("[HEALTH] Database connectivity check failed: %s", db_error)

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        **({"database_error": db_error} if db_error else {}),
    }


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


@app.options("/debug/cors-preflight")
async def debug_cors_preflight(request: Request):
    """Explicit OPTIONS endpoint for manual preflight testing.

    Send a preflight request to this endpoint to inspect exactly which
    Access-Control-Allow-Origin header the server returns for a given Origin.
    CORSMiddleware handles the real preflight logic; this endpoint exists so
    the route is registered and the middleware is guaranteed to run.

    Example:
        curl -i -X OPTIONS https://issue-tracker.railway.app/debug/cors-preflight \\
             -H "Origin: http://localhost:3000" \\
             -H "Access-Control-Request-Method: GET"
    """
    origin = request.headers.get("origin", "<no Origin header>")
    logger.info("[CORS-DEBUG] Manual preflight probe  |  Origin: %s", origin)
    # CORSMiddleware intercepts OPTIONS requests before they reach here when
    # the route is matched, so this body is only reached for non-preflight
    # OPTIONS calls.  Either way, return the diagnostic payload.
    return {
        "probe": "cors-preflight",
        "received_origin": origin,
        "effective_origins": settings.get_cors_origins(),
        "note": (
            "Check the Access-Control-Allow-Origin response header above. "
            "If it does not match your Origin, the origin is not in the "
            "allow-list or an upstream proxy is overwriting the header."
        ),
    }
