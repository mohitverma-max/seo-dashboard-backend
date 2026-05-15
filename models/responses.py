from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum


class WorkflowStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ERROR = "error"


class BaseResponse(BaseModel):
    success: bool
    message: str


class HealthResponse(BaseResponse):
    version: str
    agents: dict[str, str]  # agent_name → status


class TaskResponse(BaseResponse):
    task_id: str
    status: WorkflowStatus
    loading: bool = False
    data: Optional[Any] = None
    error: Optional[str] = None


class WorkflowStateResponse(BaseModel):
    task_id: str
    status: WorkflowStatus
    loading: bool
    result: Optional[Any] = None
    feedback_history: list[str] = []
    error: Optional[str] = None
