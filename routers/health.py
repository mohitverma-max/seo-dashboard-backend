import httpx
import os
from fastapi import APIRouter
from models.responses import HealthResponse

router = APIRouter()

_AGENTS = {
    "seo_monitor": os.getenv("SEO_MONITOR_AGENT_URL", "http://localhost:8001"),
    "content_optimizer": os.getenv("CONTENT_OPTIMIZER_AGENT_URL", "http://localhost:8002"),
    # Future agents — add here as they come online:
    # "content_writer": os.getenv("CONTENT_WRITER_AGENT_URL", "http://localhost:8003"),
    # "keyword_research": os.getenv("KEYWORD_RESEARCH_AGENT_URL", "http://localhost:8004"),
    # "technical_seo": os.getenv("TECHNICAL_SEO_AGENT_URL", "http://localhost:8005"),
}


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Returns the backend status and reachability of each connected agent."""
    agent_statuses: dict[str, str] = {}

    async with httpx.AsyncClient(timeout=3) as client:
        for name, url in _AGENTS.items():
            try:
                r = await client.get(f"{url}/health")
                agent_statuses[name] = "online" if r.status_code == 200 else f"error ({r.status_code})"
            except Exception:
                agent_statuses[name] = "offline"

    return HealthResponse(
        success=True,
        message="SEO Dashboard Backend is running.",
        version="1.0.0",
        agents=agent_statuses,
    )
