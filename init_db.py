"""
Database initialization script for the Todo application.

This script creates all database tables defined in SQLModel models.
Run this script once before starting the FastAPI application for the first time.

Usage:
    python init_db.py

Requirements:
    - .env file must be configured with DATABASE_URL
    - PostgreSQL database must be accessible
"""

import asyncio
import sys
import platform
from pathlib import Path

# Add the backend directory to Python path to allow imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Fix for Windows: psycopg requires SelectorEventLoop instead of ProactorEventLoop
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def initialize_database() -> None:
    """
    Initialize the database by creating all tables.

    This function imports the create_db_and_tables function and executes it.
    All SQLModel models are automatically discovered and their tables created.

    Raises:
        Exception: If database initialization fails
    """
    try:
        print("=" * 60)
        print("Todo Application - Database Initialization")
        print("=" * 60)
        print()

        # Import here to ensure environment variables are loaded first
        from app.database import create_db_and_tables

        print("[*] Connecting to database...")
        print("[*] Creating tables (if they don't exist)...")
        print()

        # Create all tables
        await create_db_and_tables()

        print("=" * 60)
        print("[SUCCESS] Database tables created successfully!")
        print("=" * 60)
        print()
        print("Tables created:")
        print("  - users")
        print("  - tasks")
        print()
        print("You can now start the FastAPI application:")
        print("  uvicorn main:app --reload")
        print()

    except ImportError as e:
        print("=" * 60)
        print("[ERROR] Failed to import required modules")
        print("=" * 60)
        print()
        print(f"Details: {e}")
        print()
        print("Make sure you are running this script from the backend directory:")
        print("  cd backend")
        print("  python init_db.py")
        print()
        sys.exit(1)

    except ValueError as e:
        print("=" * 60)
        print("[ERROR] Configuration error")
        print("=" * 60)
        print()
        print(f"Details: {e}")
        print()
        print("Please check your .env file and ensure:")
        print("  - DATABASE_URL is set correctly")
        print("  - BETTER_AUTH_SECRET is at least 32 characters")
        print()
        print("Example .env configuration:")
        print("  DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname")
        print("  BETTER_AUTH_SECRET=your-secret-key-at-least-32-chars-long")
        print()
        sys.exit(1)

    except Exception as e:
        print("=" * 60)
        print("[ERROR] Database initialization failed")
        print("=" * 60)
        print()
        print(f"Details: {e}")
        print()
        print("Common issues:")
        print("  - Database server is not running")
        print("  - Invalid database credentials in DATABASE_URL")
        print("  - Network connectivity issues")
        print("  - Insufficient database permissions")
        print()
        print("Please verify:")
        print("  1. PostgreSQL/Neon database is accessible")
        print("  2. DATABASE_URL in .env is correct")
        print("  3. Database user has CREATE TABLE permissions")
        print()
        sys.exit(1)


def main() -> None:
    """
    Main entry point for the database initialization script.

    This function runs the async initialize_database function using asyncio.run().
    """
    try:
        # Run the async initialization function
        asyncio.run(initialize_database())
    except KeyboardInterrupt:
        print()
        print("[WARNING] Database initialization cancelled by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
