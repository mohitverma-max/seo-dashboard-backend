from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.requests import RunMonitorRequest
from models.responses import TaskResponse, WorkflowStatus
from services.workflow import workflow_manager
from agents import seo_monitor
from utils.logger import logger

router = APIRouter()


@router.post("/run-monitor", response_model=TaskResponse, summary="Trigger SEO Monitor Agent")
async def run_monitor(body: RunMonitorRequest, background_tasks: BackgroundTasks):
    """
    Kicks off an SEO audit via the SEO Monitor Agent.

    Returns immediately with a task_id and status=running.
    The audit result is stored in the workflow state; poll /tasks/{task_id}
    or wait for the pending_approval status.
    """
    state = workflow_manager.create_task("monitor")
    workflow_manager.mark_running(state.task_id)

    logger.info(f"[{state.task_id}] Starting SEO monitor for {body.url}")

    background_tasks.add_task(
        _run_monitor_task,
        task_id=state.task_id,
        url=body.url,
        keywords=body.keywords,
        depth=body.depth,
    )

    return TaskResponse(
        success=True,
        message="SEO monitor started.",
        task_id=state.task_id,
        status=WorkflowStatus.RUNNING,
        loading=True,
    )


async def _run_monitor_task(task_id: str, url: str, keywords: list, depth: int):
    try:
        result = await seo_monitor.run_monitor(url=url, keywords=keywords, depth=depth)
        workflow_manager.mark_pending(task_id, result)
        logger.info(f"[{task_id}] Monitor complete — awaiting approval.")
    except Exception as exc:
        workflow_manager.mark_error(task_id, str(exc))
        logger.error(f"[{task_id}] Monitor failed: {exc}")
