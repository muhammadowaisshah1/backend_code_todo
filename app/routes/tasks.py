"""
Task routes for CRUD operations on todo items.

Endpoints:
- GET /api/tasks - List all tasks for current user
- POST /api/tasks - Create a new task
- GET /api/tasks/{task_id} - Get a specific task
- PUT /api/tasks/{task_id} - Update a task
- PATCH /api/tasks/{task_id}/complete - Toggle task completion status
- DELETE /api/tasks/{task_id} - Delete a task
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.dependencies import get_db, get_current_user
from app.models import User, Task
from app.schemas import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskListResponse,
)

router = APIRouter()


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    completed: bool | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    List all tasks for the current user.

    Args:
        completed: Optional filter by completion status
        current_user: Current authenticated user
        session: Database session

    Returns:
        TaskListResponse with list of tasks and total count
    """
    # Build query
    query = select(Task).where(Task.user_id == current_user.id)

    # Apply completion filter if provided
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Order by creation date (newest first)
    query = query.order_by(Task.created_at.desc())

    # Execute query
    result = await session.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new task for the current user.

    Args:
        task_data: Task creation data (title, description)
        current_user: Current authenticated user
        session: Database session

    Returns:
        TaskResponse with created task information
    """
    # Create new task
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return TaskResponse.model_validate(new_task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        TaskResponse with task information

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
    # Fetch task
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update an existing task.

    Args:
        task_id: Task ID
        task_data: Task update data (title, description, completed)
        current_user: Current authenticated user
        session: Database session

    Returns:
        TaskResponse with updated task information

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
    # Fetch task
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title

    if task_data.description is not None:
        task.description = task_data.description

    if task_data.completed is not None:
        task.completed = task_data.completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a task.

    Args:
        task_id: Task ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
    # Fetch task
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Delete task
    await session.delete(task)
    await session.commit()

    return None


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Toggle the completion status of a task.

    Args:
        task_id: Task ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        TaskResponse with updated task information

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
    # Fetch task
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Toggle completion status
    task.completed = not task.completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskResponse.model_validate(task)
