from fastapi import APIRouter, HTTPException
from models.requests import FeedbackRequest
from models.responses import TaskResponse
from services.workflow import workflow_manager
from utils.logger import logger

router = APIRouter()


@router.post("/apply-feedback", response_model=TaskResponse, summary="Apply human feedback to a task")
async def apply_feedback(body: FeedbackRequest):
    """
    Records human feedback against a task.

    The feedback is stored in the task's history and forwarded to the
    relevant agent the next time /optimize is called with this task_id.
    """
    try:
        state = workflow_manager.add_feedback(body.task_id, body.feedback)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    logger.info(f"[{body.task_id}] Feedback recorded: {body.feedback[:80]}")

    return TaskResponse(
        success=True,
        message="Feedback recorded successfully.",
        task_id=state.task_id,
        status=state.status,
        loading=state.loading,
        data={"feedback_count": len(state.feedback_history)},
    )
