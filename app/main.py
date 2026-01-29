"""
Main FastAPI application for the Todo API.

This module initializes the FastAPI app with:
- CORS middleware configured from settings
- Database lifecycle management (startup/shutdown)
- API route registration
- OpenAPI documentation

The application uses a lifespan context manager to handle:
- Startup: Create database tables
- Shutdown: Close database connections
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_db_and_tables, close_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events:
    - Startup: Create database tables if they don't exist
    - Shutdown: Close database connections gracefully

    Args:
        app: FastAPI application instance

    Yields:
        None: Control back to the application during its lifetime
    """
    # Startup: Create database tables
    print("Starting up: Creating database tables...")
    await create_db_and_tables()
    print("Database tables created successfully")

    yield

    # Shutdown: Close database connections
    print("Shutting down: Closing database connections...")
    await close_db()
    print("Database connections closed")


# Initialize FastAPI application with metadata from settings
app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack todo application API with JWT authentication",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware with origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """
    Root endpoint - API health check.

    Returns:
        dict: Welcome message, version, and API status
    """
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status
    """
    return {"status": "healthy"}


# Import and register API routers
from app.routes import auth, tasks  # noqa: E402

app.include_router(auth.router)
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
