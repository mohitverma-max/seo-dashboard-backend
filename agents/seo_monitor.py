"""
Connector for the SEO Monitor Agent.

The agent is expected to expose a POST /analyze endpoint.
If the agent is not running, the connector returns a mock result so
the rest of the backend can still be developed and tested independently.
"""

import os
import httpx
from utils.logger import logger

AGENT_URL = os.getenv("SEO_MONITOR_AGENT_URL", "http://localhost:8001")
TIMEOUT = 60  # seconds — SEO audits can be slow


async def run_monitor(url: str, keywords: list[str], depth: int) -> dict:
    """Call the SEO Monitor Agent and return its result dict."""
    payload = {"url": url, "keywords": keywords, "depth": depth}

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            logger.info(f"Calling SEO Monitor Agent at {AGENT_URL}/analyze")
            response = await client.post(f"{AGENT_URL}/analyze", json=payload)
            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        logger.warning("SEO Monitor Agent is offline — returning mock result.")
        return _mock_result(url, keywords)

    except httpx.HTTPStatusError as exc:
        # 404 means the agent is up but the endpoint isn't wired yet; fall back to mock.
        if exc.response.status_code == 404:
            logger.warning("SEO Monitor Agent /analyze not found — returning mock result.")
            return _mock_result(url, keywords)
        raise RuntimeError(
            f"SEO Monitor Agent returned {exc.response.status_code}: {exc.response.text}"
        )

    except Exception as exc:
        raise RuntimeError(f"Unexpected error calling SEO Monitor Agent: {exc}")


def _mock_result(url: str, keywords: list[str]) -> dict:
    """Stub result used when the agent is not reachable."""
    return {
        "source": "mock",
        "url": url,
        "seo_score": 72,
        "issues": [
            {"type": "missing_meta_description", "severity": "high", "count": 3},
            {"type": "slow_page_speed", "severity": "medium", "pages": ["/blog"]},
            {"type": "broken_links", "severity": "low", "count": 1},
        ],
        "keyword_positions": {kw: None for kw in keywords},
        "recommendations": [
            "Add meta descriptions to all pages.",
            "Compress images on /blog to improve LCP.",
            "Fix 1 broken internal link.",
        ],
    }
