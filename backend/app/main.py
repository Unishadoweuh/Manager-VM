from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import logger
from app.api.v1 import auth, users, vms, templates, payments, admin, monitoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Uni-Manager API...")
    # await init_db()  # Uncomment if not using Alembic
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Uni-Manager API...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan
)

# CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Health check
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Uni-Manager API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["users"])
app.include_router(vms.router, prefix=settings.API_V1_PREFIX, tags=["vms"])
app.include_router(templates.router, prefix=settings.API_V1_PREFIX, tags=["templates"])
app.include_router(payments.router, prefix=settings.API_V1_PREFIX, tags=["payments"])
app.include_router(admin.router, prefix=settings.API_V1_PREFIX, tags=["admin"])
app.include_router(monitoring.router, prefix=settings.API_V1_PREFIX, tags=["monitoring"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
