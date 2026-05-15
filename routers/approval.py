from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from models.requests import ApprovalRequest
from models.responses import TaskResponse, WorkflowStatus
from services.workflow import workflow_manager
from services.pdf_service import save_report_pdf
from utils.logger import logger

router = APIRouter()


@router.post("/approve", response_model=TaskResponse, summary="Approve a pending task")
async def approve(body: ApprovalRequest):
    """
    Marks a task as approved and generates a PDF report.

    The report download URL is returned in the response data.
    Only tasks in pending_approval status can be approved.
    """
    try:
        state = workflow_manager.require_task(body.task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if state.status != WorkflowStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail=f"Task is '{state.status}', expected 'pending_approval'.",
        )

    workflow_manager.mark_approved(body.task_id, note=body.note)

    # Generate PDF report for approved tasks
    pdf_filename = None
    try:
        result_dict = state.result if isinstance(state.result, dict) else {"result": str(state.result)}
        pdf_filename = save_report_pdf(body.task_id, result_dict)
        logger.info(f"[{body.task_id}] PDF report generated: {pdf_filename}")
    except Exception as exc:
        logger.warning(f"[{body.task_id}] PDF generation skipped: {exc}")

    logger.info(f"[{body.task_id}] Task approved.")

    return TaskResponse(
        success=True,
        message="Task approved.",
        task_id=body.task_id,
        status=WorkflowStatus.APPROVED,
        loading=False,
        data={
            "pdf_url": f"/static/pdfs/{pdf_filename}" if pdf_filename else None,
            "note": body.note,
        },
    )


@router.post("/reject", response_model=TaskResponse, summary="Reject a pending task")
async def reject(body: ApprovalRequest):
    """
    Marks a task as rejected.

    Include a note explaining why so the agent can incorporate it as
    feedback on the next run.
    """
    try:
        state = workflow_manager.require_task(body.task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if state.status not in (WorkflowStatus.PENDING_APPROVAL, WorkflowStatus.APPROVED):
        raise HTTPException(
            status_code=400,
            detail=f"Task is '{state.status}', cannot be rejected from this state.",
        )

    workflow_manager.mark_rejected(body.task_id, note=body.note)
    logger.info(f"[{body.task_id}] Task rejected. Note: {body.note}")

    return TaskResponse(
        success=True,
        message="Task rejected.",
        task_id=body.task_id,
        status=WorkflowStatus.REJECTED,
        loading=False,
        data={"note": body.note},
    )


@router.get("/tasks", summary="List all workflow tasks")
async def list_tasks():
    """Returns all tasks and their current state — useful for dashboard polling."""
    return {"success": True, "tasks": workflow_manager.list_tasks()}


@router.get("/tasks/{task_id}", summary="Get a single task state")
async def get_task(task_id: str):
    """Returns the current state of a single task."""
    try:
        state = workflow_manager.require_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"success": True, "task": state.to_dict()}


@router.get("/tasks/{task_id}/pdf", summary="Download the PDF report for an approved task")
async def download_pdf(task_id: str) -> FileResponse:
    """Streams the PDF report for an approved task."""
    from services.pdf_service import get_pdf_response
    return get_pdf_response(f"report-{task_id}.pdf")
