"""
Connector for the Content Optimizer Agent.

The agent is expected to expose a POST /optimize endpoint.
Falls back to a mock when the agent is not running.
"""

import os
import httpx
from utils.logger import logger

AGENT_URL = os.getenv("CONTENT_OPTIMIZER_AGENT_URL", "http://localhost:8002")
TIMEOUT = 60


async def optimize_content(content: str, target_keyword: str, feedback: list[str]) -> dict:
    """Call the Content Optimizer Agent and return its result dict."""
    payload = {
        "content": content,
        "target_keyword": target_keyword,
        "feedback": feedback,
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            logger.info(f"Calling Content Optimizer Agent at {AGENT_URL}/optimize")
            response = await client.post(f"{AGENT_URL}/optimize", json=payload)
            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        logger.warning("Content Optimizer Agent is offline — returning mock result.")
        return _mock_result(content, target_keyword)

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.warning("Content Optimizer Agent /optimize not found — returning mock result.")
            return _mock_result(content, target_keyword)
        raise RuntimeError(
            f"Content Optimizer Agent returned {exc.response.status_code}: {exc.response.text}"
        )

    except Exception as exc:
        raise RuntimeError(f"Unexpected error calling Content Optimizer Agent: {exc}")


def _mock_result(content: str, target_keyword: str) -> dict:
    return {
        "source": "mock",
        "target_keyword": target_keyword,
        "original_word_count": len(content.split()),
        "optimized_content": content + f"\n\n<!-- Optimized for: {target_keyword} -->",
        "readability_score": 68,
        "keyword_density": 1.4,
        "suggestions": [
            f"Use '{target_keyword}' in the H1 tag.",
            "Add 2–3 internal links.",
            "Expand the content to at least 800 words.",
        ],
    }


# ── Stubs for future agents ───────────────────────────────────────────────────
# Uncomment and implement when the agents are ready.

# async def write_content(...) -> dict:  # Content Writer Agent
#     ...

# async def research_keywords(...) -> dict:  # Keyword Research Agent
#     ...

# async def run_technical_seo(...) -> dict:  # Technical SEO Agent
#     ...
