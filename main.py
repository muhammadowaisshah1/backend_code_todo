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
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import create_db_and_tables, close_db
from app.config import settings

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
    print("Starting up: Creating database tables...")
    await create_db_and_tables()
    print("Database tables created successfully")

    yield

    # Shutdown: Close database connections
    print("Shutting down: Closing database connections...")
    await close_db()
    print("Database connections closed")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack todo application API with JWT authentication",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
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
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Health status
    """
    return {"status": "healthy"}


# Include routers
from app.routes import auth, tasks

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
