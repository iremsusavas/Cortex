"""Cortex - Multi-Agent Research Platform. FastAPI application entry point."""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.api.routes import research, stream, reports, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    try:
        from backend.db.session import init_db

        await init_db()
    except Exception:
        pass  # DB init optional for in-memory mode
    yield
    # Shutdown - graceful cleanup
    pass


app = FastAPI(
    title="Cortex",
    description="Multi-Agent Research Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request for logging."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    from fastapi.responses import JSONResponse

    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "detail": str(exc),
        },
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "cortex"}


# API routes
app.include_router(research.router, prefix=settings.API_V1_PREFIX, tags=["research"])
app.include_router(stream.router, prefix=settings.API_V1_PREFIX, tags=["stream"])
app.include_router(reports.router, prefix=settings.API_V1_PREFIX, tags=["reports"])
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX, tags=["analytics"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
