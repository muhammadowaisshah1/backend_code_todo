"""
Pydantic schemas for request/response validation.

This module defines the data models used for:
- API request validation
- API response serialization
- Type safety and documentation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


# ========================================
# Task Schemas
# ========================================

class TaskCreateRequest(BaseModel):
    """
    Schema for creating a new task.

    Attributes:
        title: Task title (required, 1-200 chars)
        description: Optional task description (max 1000 chars)
        category: Optional task category (e.g., work, personal, shopping)
        priority: Task priority level (low, medium, high) - defaults to medium
        due_date: Optional task deadline
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(default="medium", pattern="^(low|medium|high)$")
    due_date: Optional[datetime] = None


class TaskUpdateRequest(BaseModel):
    """
    Schema for updating an existing task.
    All fields are optional to allow partial updates.

    Attributes:
        title: New task title
        description: New task description
        completed: New completion status
        category: New task category
        priority: New task priority level (low, medium, high)
        due_date: New task deadline
        order: New custom order position
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    due_date: Optional[datetime] = None
    order: Optional[int] = None


class TaskResponse(BaseModel):
    """
    Schema for task response data.

    Attributes:
        id: Task ID
        user_id: Owner's user ID
        title: Task title
        description: Task description
        completed: Completion status
        created_at: Creation timestamp
        updated_at: Last update timestamp
        category: Task category
        priority: Task priority level
        due_date: Task deadline
        order: Custom order position
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    order: int


class TaskListResponse(BaseModel):
    """
    Schema for paginated task list response.
    
    Attributes:
        tasks: List of tasks
        total: Total count of tasks
    """
    tasks: list[TaskResponse]
    total: int


# ========================================
# User/Auth Schemas
# ========================================

class UserCreateRequest(BaseModel):
    """
    Schema for user registration.
    
    Attributes:
        email: User email (validated)
        name: User display name
        password: User password (min 8 chars)
    """
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=8)


class UserLoginRequest(BaseModel):
    """
    Schema for user login.
    
    Attributes:
        email: User email
        password: User password
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema for user response data.
    
    Attributes:
        id: User ID (UUID)
        email: User email
        name: User display name
        created_at: Registration timestamp
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    name: str
    created_at: datetime


class TokenResponse(BaseModel):
    """
    Schema for JWT token response.
    
    Attributes:
        access_token: JWT access token
        token_type: Token type (always "bearer")
        user: User information
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse