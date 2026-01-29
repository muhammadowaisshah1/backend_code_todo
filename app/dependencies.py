"""
Dependency injection functions for FastAPI routes.

This module provides reusable dependencies for:
- Database session management
- User authentication and authorization
- Request validation

Usage in routes:
    from app.dependencies import get_db, get_current_user

    @router.get("/tasks")
    async def get_tasks(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
    ):
        ...
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_session
from app.models import User
from app.config import settings


# ========================================
# Security Scheme
# ========================================

# HTTP Bearer token scheme for JWT authentication
security = HTTPBearer()


# ========================================
# Database Dependencies
# ========================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide database sessions to route handlers.

    This is a wrapper around get_session from app.database that provides
    a consistent interface for dependency injection.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session with automatic commit/rollback handling

    Notes:
        - Session is automatically committed on success
        - Session is automatically rolled back on exception
        - Session is always closed after the request
    """
    async for session in get_session():
        yield session


# ========================================
# Authentication Dependencies
# ========================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    This dependency:
    1. Extracts the Bearer token from the Authorization header
    2. Validates and decodes the JWT token
    3. Extracts the user_id from the token payload
    4. Queries the database for the user
    5. Returns the User object or raises 401 if invalid

    Usage:
        @router.get("/profile")
        async def get_profile(user: User = Depends(get_current_user)):
            return {"user_id": user.id, "email": user.email}

    Args:
        credentials: HTTP Authorization header with Bearer token
        db: Database session (injected via get_db dependency)

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found

    Token Payload Expected Format:
        {
            "sub": "user_id_string",  # User ID
            "exp": 1234567890,         # Expiration timestamp
            ...
        }
    """
    # Extract the JWT token from credentials
    token = credentials.credentials

    # Define credentials exception for reuse
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify the JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user_id from the "sub" (subject) claim
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        # Token is invalid, expired, or malformed
        raise credentials_exception

    # Query database for the user
    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

    except Exception as e:
        # Database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching user"
        )

    # User not found in database
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ========================================
# Optional: User Authorization Helpers
# ========================================

def verify_user_access(current_user: User, resource_user_id: str) -> None:
    """
    Helper function to verify that the current user has access to a resource.

    This ensures users can only access their own resources.

    Usage:
        @router.get("/tasks/{task_id}")
        async def get_task(
            task_id: int,
            user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            task = await get_task_by_id(db, task_id)
            verify_user_access(user, task.user_id)
            return task

    Args:
        current_user: The authenticated user
        resource_user_id: The user_id that owns the resource

    Raises:
        HTTPException 403: If user doesn't have access to the resource
    """
    if current_user.id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
