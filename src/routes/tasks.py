"""Task CRUD endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query, Response, status

from src.models.task import Task, TaskCreate, TaskStatus, TaskUpdate
from src.storage import store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[Task], status_code=status.HTTP_200_OK)
def list_tasks(
    status_filter: TaskStatus | None = Query(
        default=None,
        alias="status",
        description="Optional status filter: todo, in_progress, or done",
    ),
) -> list[Task]:
    """List tasks, optionally filtered by status (`?status=todo|in_progress|done`)."""
    tasks = store.list_tasks(status=status_filter)
    logger.info("Listed %s tasks (status=%s)", len(tasks), status_filter)
    return tasks


@router.get("/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def get_task(task_id: str) -> Task:
    task = store.get(task_id)
    if task is None:
        logger.warning("Task not found: %s", task_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    task = store.create(payload)
    logger.info("Created task %s", task.id)
    return task


@router.put("/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def update_task(task_id: str, payload: TaskUpdate) -> Task:
    task = store.update(task_id, payload)
    if task is None:
        logger.warning("Task not found for update: %s", task_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    logger.info("Updated task %s", task_id)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str) -> Response:
    deleted = store.delete(task_id)
    if not deleted:
        logger.warning("Task not found for delete: %s", task_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    logger.info("Deleted task %s", task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
