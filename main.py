"""
Main FastAPI application for the Todo API.

This module initializes the FastAPI app with:
- CORS middleware for frontend communication
- Database lifecycle management
- API route registration
- Health check endpoint
"""

import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import create_db_and_tables, close_db
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fix for Windows: psycopg requires SelectorEventLoop instead of ProactorEventLoop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events:
    - Startup: Create database tables
    - Shutdown: Close database connections
    """
    # Startup: Create database tables
    try:
        logger.info("Starting up: Creating database tables...")
        await create_db_and_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        logger.warning("Continuing without database initialization...")

    yield

    # Shutdown: Close database connections
    try:
        logger.info("Shutting down: Closing database connections...")
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during database shutdown: {e}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack todo application API with JWT authentication",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Configure CORS middleware
cors_origins = settings.get_cors_origins_list()
logger.info(f"Configuring CORS with origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """
    Root endpoint - API health check.

    Returns:
        dict: Health status with app information and timestamp
            - status: Application health status
            - app_name: Application name from settings
            - version: Application version from settings
            - timestamp: Current UTC timestamp in ISO format
    """
    logger.info("Root endpoint accessed")
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "cors_origins": settings.get_cors_origins_list()
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# Include routers
try:
    from app.routes import auth, tasks
    
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
    logger.info("API routes registered successfully")
except Exception as e:
    logger.error(f"Error loading routes: {e}")
    raise


# Add startup event handler
@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("="*50)
    logger.info(f"Application: {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {'Production' if settings.is_production() else 'Development'}")
    logger.info(f"CORS Origins: {settings.get_cors_origins_list()}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("="*50)
