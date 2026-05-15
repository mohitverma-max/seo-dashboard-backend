"""
In-memory workflow state store.

Each task moves through a simple state machine:
  idle → running → pending_approval → approved | rejected
                 ↘ error

Replace the dict with Redis or a database for production use.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from models.responses import WorkflowStatus


class WorkflowState:
    def __init__(self, task_id: str, task_type: str):
        self.task_id = task_id
        self.task_type = task_type          # "monitor" | "optimize"
        self.status = WorkflowStatus.IDLE
        self.loading = False
        self.result: Optional[Any] = None
        self.feedback_history: list[str] = []
        self.error: Optional[str] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "loading": self.loading,
            "result": self.result,
            "feedback_history": self.feedback_history,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class WorkflowManager:
    """Singleton that holds all active workflow states."""

    def __init__(self):
        self._tasks: dict[str, WorkflowState] = {}

    # ── Task lifecycle ────────────────────────────────────────────────────────

    def create_task(self, task_type: str) -> WorkflowState:
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        state = WorkflowState(task_id=task_id, task_type=task_type)
        self._tasks[task_id] = state
        return state

    def get_task(self, task_id: str) -> Optional[WorkflowState]:
        return self._tasks.get(task_id)

    def require_task(self, task_id: str) -> WorkflowState:
        state = self.get_task(task_id)
        if state is None:
            raise KeyError(f"Task '{task_id}' not found.")
        return state

    # ── State transitions ─────────────────────────────────────────────────────

    def mark_running(self, task_id: str) -> WorkflowState:
        state = self.require_task(task_id)
        state.status = WorkflowStatus.RUNNING
        state.loading = True
        state.error = None
        self._touch(state)
        return state

    def mark_pending(self, task_id: str, result: Any) -> WorkflowState:
        state = self.require_task(task_id)
        state.status = WorkflowStatus.PENDING_APPROVAL
        state.loading = False
        state.result = result
        self._touch(state)
        return state

    def mark_error(self, task_id: str, error: str) -> WorkflowState:
        state = self.require_task(task_id)
        state.status = WorkflowStatus.ERROR
        state.loading = False
        state.error = error
        self._touch(state)
        return state

    def mark_approved(self, task_id: str, note: Optional[str] = None) -> WorkflowState:
        state = self.require_task(task_id)
        state.status = WorkflowStatus.APPROVED
        if note:
            state.feedback_history.append(f"[APPROVED] {note}")
        self._touch(state)
        return state

    def mark_rejected(self, task_id: str, note: Optional[str] = None) -> WorkflowState:
        state = self.require_task(task_id)
        state.status = WorkflowStatus.REJECTED
        if note:
            state.feedback_history.append(f"[REJECTED] {note}")
        self._touch(state)
        return state

    def add_feedback(self, task_id: str, feedback: str) -> WorkflowState:
        state = self.require_task(task_id)
        state.feedback_history.append(feedback)
        self._touch(state)
        return state

    def list_tasks(self) -> list[dict]:
        return [s.to_dict() for s in self._tasks.values()]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _touch(self, state: WorkflowState):
        state.updated_at = datetime.now(timezone.utc).isoformat()


# Single shared instance — imported by all routers.
workflow_manager = WorkflowManager()
