"""
Database Migration Script - Add Phase 2 Fields to Tasks Table

This script adds category, priority, due_date, and order fields to the tasks table.
All fields are nullable or have defaults to maintain backward compatibility.
"""

import asyncio
import asyncpg
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def run_migration():
    """Run SQL migration to add new task fields"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("[ERROR] DATABASE_URL not found in environment variables")
        print("Please ensure .env file exists with DATABASE_URL set")
        return False

    # Convert SQLAlchemy-style URL to standard PostgreSQL URL for asyncpg
    # Replace postgresql+psycopg:// with postgresql://
    if "postgresql+psycopg" in database_url:
        database_url = database_url.replace("postgresql+psycopg", "postgresql")
        print("[*] Converted SQLAlchemy URL format to standard PostgreSQL format")

    # Read SQL file
    sql_file = Path(__file__).parent / "001_add_task_fields.sql"

    try:
        with open(sql_file, "r") as f:
            sql = f.read()
    except FileNotFoundError:
        print(f"[ERROR] SQL file not found at {sql_file}")
        return False

    print("[...] Connecting to database...")
    print(f"[*] Database: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'Unknown'}")

    # Connect and execute
    try:
        conn = await asyncpg.connect(database_url)
        print("[OK] Connected to database")

        print("[...] Running migration...")
        await conn.execute(sql)

        print("[SUCCESS] Migration completed successfully!")
        print("\n[+] Added fields:")
        print("   - category (VARCHAR(50), nullable)")
        print("   - priority (VARCHAR(20), default='medium')")
        print("   - due_date (TIMESTAMP, nullable)")
        print("   - order (INTEGER, default=0)")
        print("\n[+] Added indexes:")
        print("   - idx_tasks_category")
        print("   - idx_tasks_priority")
        print("   - idx_tasks_due_date")
        print("   - idx_tasks_order")

        return True

    except asyncpg.PostgresError as e:
        print(f"[ERROR] Migration failed with PostgreSQL error:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Migration failed with unexpected error:")
        print(f"   {e}")
        return False
    finally:
        if 'conn' in locals():
            await conn.close()
            print("\n[-] Database connection closed")


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION - Phase 2: Add Task Fields")
    print("=" * 60)
    print()

    success = asyncio.run(run_migration())

    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] MIGRATION SUCCESSFUL")
        print("=" * 60)
        exit(0)
    else:
        print("[FAILED] MIGRATION FAILED")
        print("=" * 60)
        exit(1)
