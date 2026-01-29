"""
SQLModel database models for the Todo application.

This module defines the database schema using SQLModel ORM.
Models include User and Task entities with proper relationships.
"""

from __future__ import annotations

from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from uuid import uuid4

if TYPE_CHECKING:
    from typing import List


def generate_uuid() -> str:
    """Generate a UUID string for primary keys."""
    return str(uuid4())


# Base configuration for SQLModel
# All models will inherit from SQLModel with table=True


class User(SQLModel, table=True):
    """
    User model representing authenticated users in the system.

    Attributes:
        id: Unique identifier (UUID as string)
        email: User's email address (unique, indexed)
        name: User's display name
        hashed_password: Bcrypt hashed password (managed by Better Auth)
        created_at: Timestamp of user creation
        tasks: Relationship to user's tasks
    """
    __tablename__ = "users"

    id: Optional[str] = Field(
        default_factory=generate_uuid,
        primary_key=True,
        max_length=36
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255
    )
    name: str = Field(max_length=200)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Task(SQLModel, table=True):
    """
    Task model representing todo items.

    Attributes:
        id: Unique identifier (auto-increment)
        user_id: Foreign key to users table
        title: Task title
        description: Optional task description
        completed: Task completion status
        created_at: Timestamp of task creation
        updated_at: Timestamp of last update
        category: Optional task category (e.g., work, personal, shopping)
        priority: Task priority level (low, medium, high)
        due_date: Optional task deadline
        order: Custom ordering for drag-drop functionality
        user: Relationship to task owner
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        max_length=36
    )
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase 2 fields - Advanced task management
    category: Optional[str] = Field(default=None, max_length=50)
    priority: Optional[str] = Field(default="medium", max_length=20)
    due_date: Optional[datetime] = Field(default=None)
    order: int = Field(default=0)

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, completed={self.completed})>"
