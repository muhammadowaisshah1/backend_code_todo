"""
Database connection and session management for the Todo application.

This module handles:
- Async database engine creation
- Session management with dependency injection
- Table creation and initialization
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure your .env file with a valid PostgreSQL connection string."
    )

# Create async engine
# echo=True enables SQL query logging (disable in production)
# Use DEBUG environment variable to control SQL logging
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG_MODE,  # Only log SQL queries in debug mode
    future=True,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum overflow connections
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function for FastAPI to inject database sessions.

    Usage in FastAPI routes:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...

    Yields:
        AsyncSession: Database session for the request
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_db_and_tables():
    """
    Create all database tables defined in SQLModel models.

    This should be called on application startup.
    Tables are created only if they don't already exist.
    """
    # Import models to ensure they are registered with SQLModel
    from sqlmodel import SQLModel
    from app.models import User, Task  # noqa: F401

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db():
    """
    Close database connections.

    This should be called on application shutdown.
    """
    await engine.dispose()
