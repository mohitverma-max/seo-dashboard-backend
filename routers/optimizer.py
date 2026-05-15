from fastapi import APIRouter, BackgroundTasks
from models.requests import OptimizeRequest
from models.responses import TaskResponse, WorkflowStatus
from services.workflow import workflow_manager
from agents import content_optimizer
from utils.logger import logger

router = APIRouter()


@router.post("/optimize", response_model=TaskResponse, summary="Trigger Content Optimizer Agent")
async def optimize(body: OptimizeRequest, background_tasks: BackgroundTasks):
    """
    Sends content to the Content Optimizer Agent for SEO improvement.

    Returns immediately with a task_id and status=running.
    Feedback from previous runs (if task_id is provided) is forwarded automatically.
    """
    # Carry over feedback from a linked monitor task if provided
    prior_feedback: list[str] = []
    if body.task_id:
        linked = workflow_manager.get_task(body.task_id)
        if linked:
            prior_feedback = linked.feedback_history

    state = workflow_manager.create_task("optimize")
    workflow_manager.mark_running(state.task_id)

    logger.info(f"[{state.task_id}] Starting content optimization for keyword '{body.target_keyword}'")

    background_tasks.add_task(
        _run_optimize_task,
        task_id=state.task_id,
        content=body.content,
        target_keyword=body.target_keyword,
        feedback=prior_feedback,
    )

    return TaskResponse(
        success=True,
        message="Content optimization started.",
        task_id=state.task_id,
        status=WorkflowStatus.RUNNING,
        loading=True,
    )


async def _run_optimize_task(task_id: str, content: str, target_keyword: str, feedback: list[str]):
    try:
        result = await content_optimizer.optimize_content(
            content=content,
            target_keyword=target_keyword,
            feedback=feedback,
        )
        workflow_manager.mark_pending(task_id, result)
        logger.info(f"[{task_id}] Optimization complete — awaiting approval.")
    except Exception as exc:
        workflow_manager.mark_error(task_id, str(exc))
        logger.error(f"[{task_id}] Optimization failed: {exc}")
