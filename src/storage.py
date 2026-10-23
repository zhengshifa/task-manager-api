"""In-memory task storage (designed to be swappable for a real database)."""

from datetime import datetime, timezone
from threading import Lock

from src.models.task import Task, TaskCreate, TaskUpdate


class TaskStore:
    """Thread-safe in-memory repository for tasks."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._lock = Lock()

    def list_tasks(self) -> list[Task]:
        with self._lock:
            return list(self._tasks.values())

    def get(self, task_id: str) -> Task | None:
        with self._lock:
            return self._tasks.get(task_id)

    def create(self, payload: TaskCreate) -> Task:
        task = Task.create(payload)
        with self._lock:
            self._tasks[task.id] = task
        return task

    def update(self, task_id: str, payload: TaskUpdate) -> Task | None:
        with self._lock:
            existing = self._tasks.get(task_id)
            if existing is None:
                return None

            data = existing.model_dump()
            updates = payload.model_dump(exclude_unset=True)
            data.update(updates)
            data["updated_at"] = datetime.now(timezone.utc)
            updated = Task(**data)
            self._tasks[task_id] = updated
            return updated

    def delete(self, task_id: str) -> bool:
        with self._lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            return True

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()


store = TaskStore()
